# ParentBridge API Testing Guide & Sample Data
**Base URL:** `http://127.0.0.1:8000`  
**Interactive Swagger UI Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
**ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Testing the Workflow Overview
To test the complete system from start to finish, follow this order:
1. **Register Admin** ➔ Get Admin Token.
2. **Create Users** (Class Teacher, Teacher, Student, Parent) using the Admin Token.
3. **Log in** as each role to get their respective Bearer Tokens.
4. **Test Role-Specific Endpoints** (Assignments, Attendance, Grades, Notices, Messages).

---

## 1. Authentication & Tokens (`/auth`)

### 1.1 Register Initial Administrator
* **Endpoint:** `POST /auth/register-admin`
* **Description:** Public registration to bootstrap the first administrator without needing pre-existing credentials.
* **Request Body:**
```json
{
  "full_name": "Dr. Sarah Connor",
  "email": "admin@parentbridge.com",
  "password": "AdminPassword@123",
  "phone": "+1-555-0101",
  "employee_id": "ADM-001"
}
```
* **Expected Response (`201 Created`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTk2ODhlNC1jMGE3LTQ2M2EtYWFlNS05Y2ZjYTZkMzdhYjYiLCJlbWFpbCI6ImFkbWluQHBhcmVudGJyaWRnZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJuYW1lIjoiRHIuIFNhcmFoIENvbm5vciIsImV4cCI6MTc5MTEzNjcxOCwidG9rZW5fdHlwZSI6ImFjY2VzcyJ9.JKaYkzK33lmpMMGnpi97pEb0Ebd_9rz7OcxDVc617FE",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTk2ODhlNC1jMGE3LTQ2M2EtYWFlNS05Y2ZjYTZkMzdhYjYiLCJlbWFpbCI6ImFkbWluQHBhcmVudGJyaWRnZS5jb20iLCJleHAiOjE3OTE3NDEzMzgsInRva2VuX3R5cGUiOiJyZWZyZXNoIn0.fXkYXDMVCVOQpjQJntWQtCFfcCOJc08Z4ZAFaCGhFWA",
  "token_type": "bearer",
  "role": "admin",
  "user_id": "119688e4-c0a7-463a-aae5-9cfca6d37ab6",
  "full_name": "Dr. Sarah Connor"
}
```

---

### 1.2 User Login
* **Endpoint:** `POST /auth/login`
* **Description:** Authenticates any user role and returns both a **3-minute access token** and a **7-day refresh token**.
* **Request Body:**
```json
{
  "email": "admin@parentbridge.com",
  "password": "AdminPassword@123"
}
```
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTk2ODhlNC1jMGE3LTQ2M2EtYWFlNS05Y2ZjYTZkMzdhYjYiLCJlbWFpbCI6ImFkbWluQHBhcmVudGJyaWRnZS5jb20iLCJyb2xlIjoiYWRtaW4iLCJuYW1lIjoiRHIuIFNhcmFoIENvbm5vciIsImV4cCI6MTc5MTEzNjc3MywidG9rZW5fdHlwZSI6ImFjY2VzcyJ9.FS9C5LnW78FMl5Xhg9Dsk2mE9UKj1gs40_JLjs-q8GQ",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTk2ODhlNC1jMGE3LTQ2M2EtYWFlNS05Y2ZjYTZkMzdhYjYiLCJlbWFpbCI6ImFkbWluQHBhcmVudGJyaWRnZS5jb20iLCJleHAiOjE3OTE3NDEzOTMsInRva2VuX3R5cGUiOiJyZWZyZXNoIn0.JFtPbjBJSObnxbk743RrQOjzTDoNQZ2BlRhW5j2Jraw",
  "token_type": "bearer",
  "role": "admin",
  "user_id": "119688e4-c0a7-463a-aae5-9cfca6d37ab6",
  "full_name": "Dr. Sarah Connor"
}
---

### 1.3 Refresh Access Token
* **Endpoint:** `POST /auth/refresh`
* **Description:** Exchanges a valid refresh token for a newly issued access token and rotated refresh token.
* **Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMTk2ODhlNC1jMGE3LTQ2M2EtYWFlNS05Y2ZjYTZkMzdhYjYiLCJlbWFpbCI6ImFkbWluQHBhcmVudGJyaWRnZS5jb20iLCJleHAiOjE3OTE3NDEzOTMsInRva2VuX3R5cGUiOiJyZWZyZXNoIn0.JFtPbjBJSObnxbk743RrQOjzTDoNQZ2BlRhW5j2Jraw"
}
```

---

### 1.4 Get Current User Profile
* **Endpoint:** `GET /auth/me`
* **Headers:** `Authorization: Bearer <ACCESS_TOKEN>`

---

## 2. Admin User Management (`/admin`)
> **Note:** All `/admin/*` routes require header: `Authorization: Bearer <ADMIN_ACCESS_TOKEN>`.

### 2.1 Create Class Teacher
* **Endpoint:** `POST /admin/users`
* **Request Body:**
```json
{
  "full_name": "John Keating",
  "email": "classteacher@parentbridge.com",
  "password": "TeacherPassword@123",
  "phone": "+1-555-0102",
  "role": "class_teacher",
  "employee_id": "CT-101",
  "assigned_class": "10",
  "assigned_section": "A"
}
```

---

### 2.2 Create Subject Teacher (Maths & Science)
* **Endpoint:** `POST /admin/users`
* **Request Body:**
```json
{
  "full_name": "Walter White",
  "email": "teacher@parentbridge.com",
  "password": "TeacherPassword@123",
  "phone": "+1-555-0103",
  "role": "teacher",
  "employee_id": "TCH-202",
  "qualification": "M.Sc Mathematics",
  "specialization": "Algebra & Calculus",
  "subjects": ["Mathematics", "Physics"],
  "classes": ["10", "11", "12"]
}
```

---

### 2.3 Create Student
* **Endpoint:** `POST /admin/users`
* **Request Body:**
```json
{
  "full_name": "Alex Mercer",
  "email": "student@parentbridge.com",
  "password": "StudentPassword@123",
  "phone": "+1-555-0104",
  "role": "student",
  "assigned_class": "10",
  "assigned_section": "A"
}
```

---

### 2.4 Create Parent
* **Endpoint:** `POST /admin/users`
* **Request Body:**
```json
{
  "full_name": "Thomas Mercer",
  "email": "parent@parentbridge.com",
  "password": "ParentPassword@123",
  "phone": "+1-555-0105",
  "role": "parent"
}
```

---

### 2.5 Assign Subject Teacher to Student
* **Endpoint:** `POST /admin/assign-teacher`
* **Request Body:**
```json
{
  "student_id": "<PASTE_STUDENT_UUID>",
  "teacher_id": "<PASTE_TEACHER_UUID>"
}
```

---

### 2.6 View All Users & System Statistics
* **List All Users:** `GET /admin/users`
* **Get Single User:** `GET /admin/users/{user_id}`
* **System Statistics:** `GET /admin/system-stats`
* **Unassigned Students:** `GET /admin/unassigned-students`

---

## 3. Assignments Management (`/assignments`)

### 3.1 Create Assignment
* **Endpoint:** `POST /assignments`
* **Headers:** `Authorization: Bearer <TEACHER_OR_ADMIN_TOKEN>`
* **Request Body:**
```json
{
  "title": "Quadratic Equations Homework",
  "subject": "Mathematics",
  "description": "Complete exercises 4.1 to 4.3 on pages 88-92 of the textbook.",
  "class_name": "10",
  "section": "A",
  "assigned_date": "2026-10-05",
  "due_date": "2026-10-12",
  "total_marks": 50.0,
  "attachment_url": "https://example.com/materials/math_hw_4.pdf"
}
```

---

### 3.2 List Assignments
* **Endpoint:** `GET /assignments?class_name=10&section=A&subject=Mathematics`
* **Headers:** `Authorization: Bearer <ANY_AUTH_TOKEN>`

---

### 3.3 Update Assignment
* **Endpoint:** `PUT /assignments/{assignment_id}`
* **Headers:** `Authorization: Bearer <TEACHER_OR_ADMIN_TOKEN>`
* **Request Body:**
```json
{
  "due_date": "2026-10-15",
  "total_marks": 60.0,
  "description": "Extended due date. Complete exercises 4.1 to 4.4."
}
```

---

## 4. Attendance Management (`/attendance`)

### 4.1 Mark Daily Attendance
* **Endpoint:** `POST /attendance`
* **Headers:** `Authorization: Bearer <TEACHER_OR_CLASS_TEACHER_OR_ADMIN_TOKEN>`
* **Request Body:**
```json
{
  "student_id": "<PASTE_STUDENT_UUID>",
  "date": "2026-10-05",
  "status": "Present",
  "remarks": "On time and participated actively"
}
```
*(Status options: `Present`, `Absent`, `Late`, `Excused`)*

---

### 4.2 Query Attendance History
* **Endpoint:** `GET /attendance/student/{student_id}?start_date=2026-10-01&end_date=2026-10-31`
* **Headers:** `Authorization: Bearer <AUTH_TOKEN>`

---

## 5. Grades & Progress Management (`/grades`)

### 5.1 Post Exam / Assignment Grade
* **Endpoint:** `POST /grades`
* **Headers:** `Authorization: Bearer <TEACHER_OR_ADMIN_TOKEN>`
* **Request Body:**
```json
{
  "student_id": "<PASTE_STUDENT_UUID>",
  "subject": "Mathematics",
  "exam_type": "Midterm Examination",
  "marks_obtained": 94.5,
  "total_marks": 100.0,
  "grade": "A+",
  "remarks": "Outstanding performance in analytical reasoning",
  "exam_date": "2026-10-02"
}
```

---

### 5.2 Get Student Grade History
* **Endpoint:** `GET /grades/student/{student_id}`
* **Headers:** `Authorization: Bearer <AUTH_TOKEN>`

---

## 6. Notices & Announcements (`/notices` & `/admin/notices`)

### 6.1 Publish School-Wide Notice (Admin)
* **Endpoint:** `POST /admin/notices`
* **Headers:** `Authorization: Bearer <ADMIN_TOKEN>`
* **Request Body:**
```json
{
  "title": "Annual Sports Meet 2026",
  "content": "The Annual Sports Meet will take place on October 25th. All students and parents are cordially invited.",
  "target_role": null,
  "target_class_name": null,
  "target_section": null
}
```

---

### 6.2 Publish Class Notice (Class Teacher)
* **Endpoint:** `POST /class-teacher/notices`
* **Headers:** `Authorization: Bearer <CLASS_TEACHER_TOKEN>`
* **Request Body:**
```json
{
  "title": "Science Project Submission Reminder",
  "content": "Please bring your chemistry model kits for the practical evaluation tomorrow morning.",
  "target_role": "student",
  "target_class_name": "10",
  "target_section": "A"
}
```

---

### 6.3 Fetch Accessible Notices
* **Endpoint:** `GET /notices?class_name=10&section=A`
* **Headers:** `Authorization: Bearer <ANY_AUTH_TOKEN>`

---

## 7. Direct Messaging & Real-Time Chat (`/messages` & `/ws`)

### 7.1 Send Direct Message (REST)
* **Endpoint:** `POST /messages`
* **Headers:** `Authorization: Bearer <SENDER_TOKEN>`
* **Request Body:**
```json
{
  "receiver_id": "<RECEIVER_USER_UUID>",
  "receiver_role": "teacher",
  "student_id": "<PASTE_STUDENT_UUID>",
  "subject": "Regarding Math homework doubt",
  "message": "Hello Mr. White, could you please clarify question 4 on page 90?"
}
```

---

### 7.2 Read Conversation History
* **Endpoint:** `GET /messages?other_user_id=<OTHER_USER_UUID>`
* **Headers:** `Authorization: Bearer <USER_TOKEN>`

---

### 7.3 Real-Time WebSocket Chat
* **WebSocket URL:**
  ```text
  ws://127.0.0.1:8000/ws/chat/{conversation_id}?token=<YOUR_ACCESS_TOKEN>
  ```
* **Send JSON frame:**
  ```json
  {
    "receiver_id": "<RECEIVER_USER_UUID>",
    "student_id": "<STUDENT_UUID>",
    "subject": "Quick question",
    "message": "Thank you for the explanation!"
  }
  ```

---

## 8. Role-Specific Dashboards

### 8.1 Student Portal (`/student`)
* **Headers:** `Authorization: Bearer <STUDENT_OR_ADMIN_TOKEN>`
* `GET /student/assignments` - Student's assigned tasks
* `GET /student/grades` - Report cards and subject marks
* `GET /student/attendance` - Personal attendance metrics
* `GET /student/progress` - Comprehensive GPA and performance report

---

### 8.2 Parent Portal (`/parent`)
* **Headers:** `Authorization: Bearer <PARENT_OR_ADMIN_TOKEN>`
* `GET /parent/children` - List of linked children
* `GET /parent/grades/{student_id}` - Child's grades
* `GET /parent/attendance/{student_id}` - Child's attendance record
* `GET /parent/progress/{student_id}` - Child's progress overview
* `GET /parent/teachers` - Contact details of teachers teaching their child

---

## Quick Testing Credentials Summary

| Role | Email | Password | Primary Functions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@parentbridge.com` | `AdminPassword@123` | Full control, User creation, System statistics, Global notices |
| **Class Teacher** | `classteacher@parentbridge.com` | `TeacherPassword@123` | Class roster, Daily attendance, Class announcements, Progress |
| **Teacher** | `teacher@parentbridge.com` | `TeacherPassword@123` | Homework assignments, Exam marks, Student notices |
| **Student** | `student@parentbridge.com` | `StudentPassword@123` | View assignments, Check grades & attendance, Chat |
| **Parent** | `parent@parentbridge.com` | `ParentPassword@123` | Monitor children's progress, View grades & attendance, Message teachers |
