import asyncio
import uuid
from datetime import date, datetime
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from main import app
from app.models.user import User, UserRole
from app.models.admin import Admin
from app.models.class_teacher import ClassTeacher
from app.models.teacher import Teacher
from app.models.student import Student, StudentParent
from app.models.assignment import Assignment
from app.models.grade import Grade
from app.models.attendance import Attendance
from app.models.notice import Notice
from app.models.message import Message
from app.security.password import hash_password

# 1. Compile Postgres types to SQLite for in-memory testing
@compiles(ARRAY, "sqlite")
def compile_array_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(PG_UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"

# 2. Setup Async SQLite in-memory engine
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Override get_db dependency
async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

app.dependency_overrides[get_db] = override_get_db


async def setup_test_database():
    """Create all tables and seed sample data."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # Create users
        admin_id = uuid.uuid4()
        ct_id = uuid.uuid4()
        t_id = uuid.uuid4()
        st_user_id = uuid.uuid4()
        p_user_id = uuid.uuid4()

        admin_user = User(
            user_id=admin_id,
            full_name="Principal Skinner",
            email="admin@school.com",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        ct_user = User(
            user_id=ct_id,
            full_name="Mrs. Edna Krabappel",
            email="classteacher@school.com",
            password_hash=hash_password("Teacher@123"),
            role=UserRole.CLASS_TEACHER,
            is_active=True
        )
        t_user = User(
            user_id=t_id,
            full_name="Mr. Dewey Largo",
            email="teacher@school.com",
            password_hash=hash_password("Teacher@123"),
            role=UserRole.TEACHER,
            is_active=True
        )
        student_user = User(
            user_id=st_user_id,
            full_name="Bart Simpson",
            email="student@school.com",
            password_hash=hash_password("Student@123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        parent_user = User(
            user_id=p_user_id,
            full_name="Homer Simpson",
            email="parent@school.com",
            password_hash=hash_password("Parent@123"),
            role=UserRole.PARENT,
            is_active=True
        )

        session.add_all([admin_user, ct_user, t_user, student_user, parent_user])
        await session.flush()

        # Profiles
        admin_prof = Admin(user_id=admin_id, full_name="Principal Skinner", email="admin@school.com", is_super_admin=True)
        ct_prof = ClassTeacher(user_id=ct_id, full_name="Mrs. Edna Krabappel", email="classteacher@school.com", assigned_class="10", assigned_section="A")
        t_prof = Teacher(user_id=t_id, full_name="Mr. Dewey Largo", email="teacher@school.com", subjects=["Music", "Mathematics"], classes=["10"])
        
        session.add_all([admin_prof, ct_prof, t_prof])
        await session.flush()

        # Student & Parent link
        student_prof = Student(
            student_id=uuid.uuid4(),
            user_id=st_user_id,
            full_name="Bart Simpson",
            email="student@school.com",
            class_name="10",
            section="A",
            roll_number="01",
            admission_number="ADM-1001",
            teacher_id=t_prof.teacher_id
        )
        session.add(student_prof)
        await session.flush()

        student_parent_link = StudentParent(
            student_id=student_prof.student_id,
            parent_user_id=p_user_id,
            relationship="Father"
        )
        session.add(student_parent_link)
        await session.commit()

        return {
            "admin_user_id": str(admin_id),
            "teacher_user_id": str(t_id),
            "teacher_id": str(t_prof.teacher_id),
            "student_id": str(student_prof.student_id),
            "student_user_id": str(st_user_id),
            "parent_user_id": str(p_user_id)
        }


async def run_all_tests():
    ids = await setup_test_database()
    results = []

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Helper for reporting
        def record(group: str, method: str, path: str, status_code: int, expected: int, note: str):
            success = "✅ PASS" if status_code == expected else f"❌ FAIL (Got {status_code})"
            results.append({
                "group": group,
                "method": method,
                "path": path,
                "status_code": status_code,
                "expected": expected,
                "result": success,
                "note": note
            })

        # 1. Health check
        res = await client.get("/")
        record("SYSTEM", "GET", "/", res.status_code, 200, "Root health check status")

        # 2. Auth Logins
        tokens = {}
        for role_name, email, pwd in [
            ("admin", "admin@school.com", "Admin@123"),
            ("class_teacher", "classteacher@school.com", "Teacher@123"),
            ("teacher", "teacher@school.com", "Teacher@123"),
            ("student", "student@school.com", "Student@123"),
            ("parent", "parent@school.com", "Parent@123"),
        ]:
            res = await client.post("/auth/login", json={"email": email, "password": pwd})
            record("AUTH", "POST", f"/auth/login ({role_name})", res.status_code, 200, f"Login as {role_name}")
            if res.status_code == 200:
                tokens[role_name] = res.json()["access_token"]

        admin_h = {"Authorization": f"Bearer {tokens['admin']}"}
        ct_h = {"Authorization": f"Bearer {tokens['class_teacher']}"}
        t_h = {"Authorization": f"Bearer {tokens['teacher']}"}
        s_h = {"Authorization": f"Bearer {tokens['student']}"}
        p_h = {"Authorization": f"Bearer {tokens['parent']}"}

        # 3. Auth Me
        res = await client.get("/auth/me", headers=admin_h)
        record("AUTH", "GET", "/auth/me", res.status_code, 200, "Authenticated user profile")

        # 4. Admin Users Management
        new_user_payload = {
            "full_name": "Lisa Simpson",
            "email": "lisa@school.com",
            "password": "Password@123",
            "phone": "9876543210",
            "role": "student",
            "assigned_class": "10",
            "assigned_section": "A"
        }
        res = await client.post("/admin/users", json=new_user_payload, headers=admin_h)
        record("ADMIN", "POST", "/admin/users", res.status_code, 201, "Admin creates new user account")
        created_user_id = res.json().get("user_id") if res.status_code == 201 else None

        res = await client.get("/admin/users", headers=admin_h)
        record("ADMIN", "GET", "/admin/users", res.status_code, 200, "Admin lists all users")

        if created_user_id:
            res = await client.get(f"/admin/users/{created_user_id}", headers=admin_h)
            record("ADMIN", "GET", f"/admin/users/{{user_id}}", res.status_code, 200, "Admin views specific user")

            res = await client.put(f"/admin/users/{created_user_id}", json={"full_name": "Lisa Marie Simpson"}, headers=admin_h)
            record("ADMIN", "PUT", f"/admin/users/{{user_id}}", res.status_code, 200, "Admin updates user profile")

            res = await client.delete(f"/admin/users/{created_user_id}", headers=admin_h)
            record("ADMIN", "DELETE", f"/admin/users/{{user_id}}", res.status_code, 200, "Admin deactivates user")

        res = await client.put(f"/admin/students/{ids['student_id']}/teacher", json={"teacher_id": ids['teacher_id']}, headers=admin_h)
        record("ADMIN", "PUT", "/admin/students/{id}/teacher", res.status_code, 200, "Admin assigns teacher to student")

        # 5. Admin Notices
        notice_payload = {
            "title": "Annual Sports Day",
            "content": "Sports day is scheduled for next Friday.",
            "target_role": "student",
            "target_class_name": "10"
        }
        res = await client.post("/admin/notices", json=notice_payload, headers=admin_h)
        record("ADMIN", "POST", "/admin/notices", res.status_code, 201, "Admin creates school notice")
        admin_notice_id = res.json().get("notice_id") if res.status_code == 201 else None

        res = await client.get("/admin/notices", headers=admin_h)
        record("ADMIN", "GET", "/admin/notices", res.status_code, 200, "Admin lists all notices")

        # 6. Class Teacher Routes
        res = await client.get("/class-teacher/students", headers=ct_h)
        record("CLASS_TEACHER", "GET", "/class-teacher/students", res.status_code, 200, "Class Teacher lists class students")

        res = await client.get(f"/class-teacher/students/{ids['student_id']}", headers=ct_h)
        record("CLASS_TEACHER", "GET", "/class-teacher/students/{id}", res.status_code, 200, "Class Teacher views student details")

        ct_att_payload = {
            "student_id": ids['student_id'],
            "date": "2026-10-02",
            "status": "present",
            "remarks": "On time"
        }
        res = await client.post("/class-teacher/attendance", json=ct_att_payload, headers=ct_h)
        record("CLASS_TEACHER", "POST", "/class-teacher/attendance", res.status_code, 201, "Class Teacher marks attendance")
        ct_att_id = res.json().get("attendance_id") if res.status_code == 201 else None

        if ct_att_id:
            res = await client.put(f"/class-teacher/attendance/{ct_att_id}", json={"status": "present", "remarks": "Excellent"}, headers=ct_h)
            record("CLASS_TEACHER", "PUT", "/class-teacher/attendance/{id}", res.status_code, 200, "Class Teacher updates attendance")

        res = await client.get(f"/class-teacher/marks/{ids['student_id']}", headers=ct_h)
        record("CLASS_TEACHER", "GET", "/class-teacher/marks/{id}", res.status_code, 200, "Class Teacher views cumulative marks")

        res = await client.post("/class-teacher/notices", json={"title": "Class 10A Meeting", "content": "Bring textbooks tomorrow"}, headers=ct_h)
        record("CLASS_TEACHER", "POST", "/class-teacher/notices", res.status_code, 201, "Class Teacher creates class notice")

        # 7. Teacher Routes
        res = await client.get("/teacher/students", headers=t_h)
        record("TEACHER", "GET", "/teacher/students", res.status_code, 200, "Teacher lists taught students")

        res = await client.get(f"/teacher/students/{ids['student_id']}", headers=t_h)
        record("TEACHER", "GET", "/teacher/students/{id}", res.status_code, 200, "Teacher views student details")

        res = await client.post("/teacher/notices", json={"title": "Math Quiz", "content": "Quiz on Chapter 4"}, headers=t_h)
        record("TEACHER", "POST", "/teacher/notices", res.status_code, 201, "Teacher sends subject notice")

        # 8. Assignments
        assign_payload = {
            "title": "Algebra Homework 1",
            "subject": "Mathematics",
            "description": "Solve problems 1 to 10 on page 42.",
            "class_name": "10",
            "section": "A",
            "due_date": "2026-10-10",
            "total_marks": 20.0
        }
        res = await client.post("/assignments", json=assign_payload, headers=t_h)
        record("ASSIGNMENTS", "POST", "/assignments", res.status_code, 201, "Teacher creates assignment")
        assignment_id = res.json().get("assignment_id") if res.status_code == 201 else None

        res = await client.get("/assignments", headers=t_h)
        record("ASSIGNMENTS", "GET", "/assignments", res.status_code, 200, "List assignments")

        if assignment_id:
            res = await client.get(f"/assignments/{assignment_id}", headers=t_h)
            record("ASSIGNMENTS", "GET", "/assignments/{id}", res.status_code, 200, "View assignment details")

            res = await client.put(f"/assignments/{assignment_id}", json={"title": "Algebra Homework 1 (Updated)"}, headers=t_h)
            record("ASSIGNMENTS", "PUT", "/assignments/{id}", res.status_code, 200, "Update assignment")

        # 9. Grades
        grade_payload = {
            "student_id": ids['student_id'],
            "subject": "Mathematics",
            "exam_type": "Unit Test",
            "marks_obtained": 18.5,
            "total_marks": 20.0,
            "remarks": "Well done"
        }
        res = await client.post("/grades", json=grade_payload, headers=t_h)
        record("GRADES", "POST", "/grades", res.status_code, 201, "Teacher records student grade")
        grade_id = res.json().get("grade_id") if res.status_code == 201 else None

        if grade_id:
            res = await client.put(f"/grades/{grade_id}", json={"marks_obtained": 19.0}, headers=t_h)
            record("GRADES", "PUT", "/grades/{id}", res.status_code, 200, "Teacher updates student grade")

        res = await client.get(f"/grades/student/{ids['student_id']}", headers=t_h)
        record("GRADES", "GET", "/grades/student/{id}", res.status_code, 200, "List student grades")

        # 10. Attendance
        teacher_att_payload = {
            "student_id": ids['student_id'],
            "date": "2026-10-03",
            "status": "present",
            "remarks": "Attended lab"
        }
        res = await client.post("/attendance", json=teacher_att_payload, headers=t_h)
        record("ATTENDANCE", "POST", "/attendance", res.status_code, 201, "Teacher records daily attendance")

        res = await client.get(f"/attendance/student/{ids['student_id']}", headers=t_h)
        record("ATTENDANCE", "GET", "/attendance/student/{id}", res.status_code, 200, "List student attendance")

        # 11. Parent Endpoints
        res = await client.get("/parent/children", headers=p_h)
        record("PARENT", "GET", "/parent/children", res.status_code, 200, "Parent views linked children")

        res = await client.get(f"/parent/children/{ids['student_id']}/assignments", headers=p_h)
        record("PARENT", "GET", "/parent/children/{id}/assignments", res.status_code, 200, "Parent views child's assignments")

        res = await client.get(f"/parent/children/{ids['student_id']}/grades", headers=p_h)
        record("PARENT", "GET", "/parent/children/{id}/grades", res.status_code, 200, "Parent views child's grades")

        res = await client.get(f"/parent/children/{ids['student_id']}/attendance", headers=p_h)
        record("PARENT", "GET", "/parent/children/{id}/attendance", res.status_code, 200, "Parent views child's attendance")

        res = await client.get(f"/parent/children/{ids['student_id']}/progress", headers=p_h)
        record("PARENT", "GET", "/parent/children/{id}/progress", res.status_code, 200, "Parent views child's progress & %")

        # 12. Student Endpoints
        res = await client.get("/student/assignments", headers=s_h)
        record("STUDENT", "GET", "/student/assignments", res.status_code, 200, "Student views own assignments")

        res = await client.get("/student/grades", headers=s_h)
        record("STUDENT", "GET", "/student/grades", res.status_code, 200, "Student views own grades")

        res = await client.get("/student/attendance", headers=s_h)
        record("STUDENT", "GET", "/student/attendance", res.status_code, 200, "Student views own attendance")

        res = await client.get("/student/progress", headers=s_h)
        record("STUDENT", "GET", "/student/progress", res.status_code, 200, "Student views own progress & %")

        # 13. Public/Role-Aware Notices
        res = await client.get("/notices", headers=s_h)
        record("NOTICES", "GET", "/notices", res.status_code, 200, "Fetch role-permitted notices")

        # 14. Messages REST
        msg_payload = {
            "receiver_id": ids['teacher_user_id'],
            "receiver_role": "teacher",
            "student_id": ids['student_id'],
            "subject": "Math progress inquiry",
            "message": "Hello Mr. Largo, could you please provide feedback on Bart's algebra homework?"
        }
        res = await client.post("/messages", json=msg_payload, headers=p_h)
        record("MESSAGES", "POST", "/messages", res.status_code, 201, "Parent sends message to Teacher")
        msg_id = res.json().get("message_id") if res.status_code == 201 else None

        res = await client.get("/messages", headers=t_h)
        record("MESSAGES", "GET", "/messages", res.status_code, 200, "Teacher lists conversation messages")

        if msg_id:
            res = await client.get(f"/messages/{msg_id}", headers=t_h)
            record("MESSAGES", "GET", "/messages/{id}", res.status_code, 200, "Teacher reads message")

            res = await client.put(f"/messages/{msg_id}/read", headers=t_h)
            record("MESSAGES", "PUT", "/messages/{id}/read", res.status_code, 200, "Teacher marks message as read")

    return results


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    print("\n" + "="*80)
    print(f"{'GROUP':<15} | {'METHOD':<6} | {'ENDPOINT':<38} | {'STATUS':<6} | {'RESULT'}")
    print("="*80)
    passed_count = 0
    for r in results:
        if "PASS" in r["result"]:
            passed_count += 1
        print(f"{r['group']:<15} | {r['method']:<6} | {r['path']:<38} | {r['status_code']:<6} | {r['result']} - {r['note']}")
    print("="*80)
    print(f"TOTAL TESTED: {len(results)} | PASSED: {passed_count} | FAILED: {len(results) - passed_count}")
