# 🏫 ParentBridge API Testing Guide & Fresh Seed Data

**Base Server URL:** `http://127.0.0.1:8000`  
**Swagger UI (Interactive API Tester):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
**ReDoc Documentation:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🌟 Brand-New Clean User Roster (No Conflicts)
Use this completely fresh dataset for a clean run without encountering `"Email already exists"` errors:

| Role | Full Name | New Email | Password | Details |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | **Principal Marcus Vance** | `principal.vance@greenwood.edu` | `AdminSecure#2026` | Employee ID: `ADM-1001` |
| **Class Teacher** | **Elena Rostova** | `elena.rostova@greenwood.edu` | `TeacherPass#2026` | Class `9`, Section `B` (ID: `CT-2001`) |
| **Subject Teacher** | **David Sterling** | `david.sterling@greenwood.edu` | `TeacherPass#2026` | Physics & Chemistry (ID: `TCH-3001`) |
| **Student** | **Ethan Hayes** | `ethan.hayes@student.greenwood.edu` | `StudentPass#2026` | Class `9`, Section `B` |
| **Parent** | **Jonathan Hayes** | `jonathan.hayes@gmail.com` | `ParentPass#2026` | Father of Ethan Hayes |

---

## 📝 Testing Scratchpad (Copy your generated IDs here)
- **`ADMIN_TOKEN`**: `___________________________`
- **`CLASS_TEACHER_ID`**: `___________________________`
- **`CLASS_TEACHER_TOKEN`**: `___________________________`
- **`TEACHER_ID`**: `___________________________`
- **`TEACHER_TOKEN`**: `___________________________`
- **`STUDENT_ID`**: `___________________________`
- **`STUDENT_TOKEN`**: `___________________________`
- **`PARENT_ID`**: `___________________________`
- **`PARENT_TOKEN`**: `___________________________`

---

## 🔑 Authentication Header
For all protected routes, include this in your request header:
```text
Authorization: Bearer <TOKEN>
```
> **Swagger UI:** Click the green **Authorize 🔓** button at the top right of [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and paste your token.

---

# 🚀 Complete Testing Procedure

---

## STEP 1: Register & Log In School Administrator

### 1.1 Register Fresh Admin
* **Method & URL:** `POST /auth/register-admin`
* **Auth Required:** None (Public bootstrap)

#### Request Body:
```json
{
  "full_name": "Principal Marcus Vance",
  "email": "principal.vance@greenwood.edu",
  "password": "AdminSecure#2026",
  "phone": "+1-555-0901",
  "employee_id": "ADM-1001"
}
```
📌 **Action:** Copy `access_token` from the response ➔ Save as **`ADMIN_TOKEN`**.

---

### 1.2 Admin Login (Verification)
* **Method & URL:** `POST /auth/login`
* **Auth Required:** None

#### Request Body:
```json
{
  "email": "principal.vance@greenwood.edu",
  "password": "AdminSecure#2026"
}
```

---

## STEP 2: Create School Staff & Users (Admin Only)
> ⚠️ **Header for all requests in this step:**  
> `Authorization: Bearer <ADMIN_TOKEN>`

---

### 2.1 Create Class Teacher (Grade 9-B)
* **Method & URL:** `POST /admin/users`

#### Request Body:
```json
{
  "full_name": "Elena Rostova",
  "email": "elena.rostova@greenwood.edu",
  "password": "TeacherPass#2026",
  "phone": "+1-555-0902",
  "role": "class_teacher",
  "employee_id": "CT-2001",
  "assigned_class": "9",
  "assigned_section": "B"
}
```
📌 **Action:** Copy `id` from the response ➔ Save as **`CLASS_TEACHER_ID`**.

---

### 2.2 Create Subject Teacher (Physics & Chemistry)
* **Method & URL:** `POST /admin/users`

#### Request Body:
```json
{
  "full_name": "David Sterling",
  "email": "david.sterling@greenwood.edu",
  "password": "TeacherPass#2026",
  "phone": "+1-555-0903",
  "role": "teacher",
  "employee_id": "TCH-3001",
  "qualification": "M.Sc Applied Physics",
  "specialization": "Kinematics & Thermodynamics",
  "subjects": ["Physics", "Chemistry"],
  "classes": ["9", "10"]
}
```
📌 **Action:** Copy `id` from the response ➔ Save as **`TEACHER_ID`**.

---

### 2.3 Create Student (Class 9-B)
* **Method & URL:** `POST /admin/users`

#### Request Body:
```json
{
  "full_name": "Ethan Hayes",
  "email": "ethan.hayes@student.greenwood.edu",
  "password": "StudentPass#2026",
  "phone": "+1-555-0904",
  "role": "student",
  "assigned_class": "9",
  "assigned_section": "B"
}
```
📌 **Action:** Copy `id` from the response ➔ Save as **`STUDENT_ID`**.

---

### 2.4 Create Parent
* **Method & URL:** `POST /admin/users`

#### Request Body:
```json
{
  "full_name": "Jonathan Hayes",
  "email": "jonathan.hayes@gmail.com",
  "password": "ParentPass#2026",
  "phone": "+1-555-0905",
  "role": "parent"
}
```
📌 **Action:** Copy `id` from the response ➔ Save as **`PARENT_ID`**.

---

### 2.5 Assign Subject Teacher to Student
* **Method & URL:** `POST /admin/assign-teacher`

#### Request Body:
```json
{
  "student_id": "<PASTE_STUDENT_ID>",
  "teacher_id": "<PASTE_TEACHER_ID>"
}
```

---

## STEP 3: Log In as Each Role to Collect Tokens
Use `POST /auth/login` to obtain each individual user's Bearer access token:

### 3.1 Class Teacher Login
```json
{
  "email": "elena.rostova@greenwood.edu",
  "password": "TeacherPass#2026"
}
```
📌 **Save token as:** **`CLASS_TEACHER_TOKEN`**

### 3.2 Subject Teacher Login
```json
{
  "email": "david.sterling@greenwood.edu",
  "password": "TeacherPass#2026"
}
```
📌 **Save token as:** **`TEACHER_TOKEN`**

### 3.3 Student Login
```json
{
  "email": "ethan.hayes@student.greenwood.edu",
  "password": "StudentPass#2026"
}
```
📌 **Save token as:** **`STUDENT_TOKEN`**

### 3.4 Parent Login
```json
{
  "email": "jonathan.hayes@gmail.com",
  "password": "ParentPass#2026"
}
```
📌 **Save token as:** **`PARENT_TOKEN`**

---

## STEP 4: Homework & Assignments (`/assignments`)

### 4.1 Teacher Publishes Physics Assignment
* **Method & URL:** `POST /assignments`
* **Header:** `Authorization: Bearer <TEACHER_TOKEN>`

#### Request Body:
```json
{
  "title": "Newton's Laws of Motion Problem Set",
  "subject": "Physics",
  "description": "Complete conceptual questions 1 through 5 and numerical problems 6 to 10 from Chapter 3.",
  "class_name": "9",
  "section": "B",
  "assigned_date": "2026-10-06",
  "due_date": "2026-10-13",
  "total_marks": 25.0,
  "attachment_url": "https://greenwood.edu/materials/physics_ch3_problems.pdf"
}
```
📌 **Action:** Note `id` from response as **`ASSIGNMENT_ID`**.

---

### 4.2 Student Checks Homework List
* **Method & URL:** `GET /student/assignments`
* **Header:** `Authorization: Bearer <STUDENT_TOKEN>`
* **Result:** Returns Newton's Laws assignment for Class 9-B.

---

## STEP 5: Daily Attendance (`/attendance`)

### 5.1 Class Teacher Marks Ethan Hayes Present
* **Method & URL:** `POST /attendance`
* **Header:** `Authorization: Bearer <CLASS_TEACHER_TOKEN>`

#### Request Body:
```json
{
  "student_id": "<PASTE_STUDENT_ID>",
  "date": "2026-10-06",
  "status": "Present",
  "remarks": "On time and participated actively in morning roll call"
}
```

---

### 5.2 Parent Checks Attendance History
* **Method & URL:** `GET /parent/attendance/<PASTE_STUDENT_ID>`
* **Header:** `Authorization: Bearer <PARENT_TOKEN>`

---

## STEP 6: Grades & Academic Reports (`/grades`)

### 6.1 Physics Teacher Posts Unit Test Grade
* **Method & URL:** `POST /grades`
* **Header:** `Authorization: Bearer <TEACHER_TOKEN>`

#### Request Body:
```json
{
  "student_id": "<PASTE_STUDENT_ID>",
  "subject": "Physics",
  "exam_type": "Unit Test 1",
  "marks_obtained": 24.0,
  "total_marks": 25.0,
  "grade": "A+",
  "remarks": "Flawless free-body diagrams and clear explanations",
  "exam_date": "2026-10-05"
}
```

---

### 6.2 Student Views Report Card
* **Method & URL:** `GET /student/grades`
* **Header:** `Authorization: Bearer <STUDENT_TOKEN>`

---

### 6.3 Parent Reviews Child's Academic Progress
* **Method & URL:** `GET /parent/progress/<PASTE_STUDENT_ID>`
* **Header:** `Authorization: Bearer <PARENT_TOKEN>`

---

## STEP 7: School Notices (`/notices`)

### 7.1 Principal Posts School Notice
* **Method & URL:** `POST /admin/notices`
* **Header:** `Authorization: Bearer <ADMIN_TOKEN>`

#### Request Body:
```json
{
  "title": "Fall Term Parent-Teacher Conference",
  "content": "The Fall Term PTC will be conducted on Saturday, October 24th from 9:00 AM to 1:00 PM.",
  "target_role": null,
  "target_class_name": null,
  "target_section": null
}
```

---

### 7.2 Class Teacher Posts Notice for Class 9-B
* **Method & URL:** `POST /class-teacher/notices`
* **Header:** `Authorization: Bearer <CLASS_TEACHER_TOKEN>`

#### Request Body:
```json
{
  "title": "Science Lab Coat Reminder",
  "content": "All Class 9-B students must bring their lab coats and safety goggles for Thursday's Chemistry lab.",
  "target_role": "student",
  "target_class_name": "9",
  "target_section": "B"
}
```

---

### 7.3 Student/Parent Checks Notices
* **Method & URL:** `GET /notices?class_name=9&section=B`
* **Header:** `Authorization: Bearer <STUDENT_TOKEN>` (or `<PARENT_TOKEN>`)

---

## STEP 8: Direct Messaging (`/messages`)

### 8.1 Parent Messages Physics Teacher
* **Method & URL:** `POST /messages`
* **Header:** `Authorization: Bearer <PARENT_TOKEN>`

#### Request Body:
```json
{
  "receiver_id": "<PASTE_TEACHER_ID>",
  "receiver_role": "teacher",
  "student_id": "<PASTE_STUDENT_ID>",
  "subject": "Extra practice material for Physics Olympiad",
  "message": "Hello Mr. Sterling, Ethan is very interested in the upcoming Physics Olympiad. Could you recommend any advanced preparation books?"
}
```

---

### 8.2 Teacher Replies to Parent
* **Method & URL:** `POST /messages`
* **Header:** `Authorization: Bearer <TEACHER_TOKEN>`

#### Request Body:
```json
{
  "receiver_id": "<PASTE_PARENT_ID>",
  "receiver_role": "parent",
  "student_id": "<PASTE_STUDENT_ID>",
  "subject": "Re: Extra practice material for Physics Olympiad",
  "message": "Hello Mr. Hayes! That's wonderful to hear. I will share a set of Olympiad past papers with Ethan in class tomorrow."
}
```
