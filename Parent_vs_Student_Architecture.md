# ParentBridge Architecture: Why Parent & Student Accounts Are Separate

## Executive Summary
In school portal systems like **ParentBridge**, keeping **Parent** and **Student** accounts distinct is a foundational architectural decision. Rather than treating parents and students as the same identity, the system separates them into distinct roles while linking them through a relational mapping table (`student_parents`).

This document details the functional, relational, security, and real-world justifications for this design.

---

## 1. Real-World Relational Scenarios

### 1.1 One Parent with Multiple Children (1-to-Many)
In real life, parents frequently have two or more children attending the same school across different grade levels (e.g., one child in 10th grade, another in 7th grade).

* **If Parent & Student were the same account:**
  - A parent would need separate credentials, emails, and passwords for each child.
  - The parent would have to log out and log back in repeatedly just to check each child's grades or homework.
* **With Separate Parent Accounts:**
  - The parent has **one single account** (e.g., `parent@example.com`).
  - Upon logging in, the parent calls `GET /parent/children` and sees all their linked children in one unified dashboard.
  - The parent can toggle between children seamlessly to view their individual attendance, progress, and assignments.

```
       +------------------------------------+
       |       Parent Account               |
       |    (e.g., Thomas Mercer)           |
       +-----------------+------------------+
                         |
            +------------+------------+
            |                         |
            v                         v
+-----------------------+ +-----------------------+
|  Child 1: Alex Mercer | |  Child 2: Emma Mercer |
|  Grade 10, Section A  | |  Grade 7, Section B   |
+-----------------------+ +-----------------------+
```

---

### 1.2 Multiple Guardians for One Student (Many-to-1)
A single student often has multiple guardians (Father, Mother, or Legal Guardian):
* Both parents can register their own accounts with their personal emails and phone numbers.
* Both guardians have direct access to monitor their child's academic health.
* The school administration can contact either guardian independently.

---

## 2. Functional & Permissions Matrix

Students and Parents interact with the educational system with completely different goals:

| Feature / Action | Student Account (`role: student`) | Parent Account (`role: parent`) |
| :--- | :--- | :--- |
| **Primary Role** | The Learner | The Guardian / Supervisor |
| **Assignments** | Views homework, instructions, deadlines, and submits work | Monitors what homework is assigned to ensure the child completes it |
| **Grades & Marks** | Reviews own exam marks and feedback | Reviews historical report cards, GPA, and subject breakdown |
| **Attendance** | Checks daily status | Tracks attendance patterns, receives absence notifications, provides excuse notes |
| **School Notices** | Receives student-targeted notices (sports days, test schedules, club activities) | Receives parent-targeted notices (Parent-Teacher meetings, fee circulars, policy changes) |
| **Scope of Data** | Restricted strictly to their own enrolled class and section | Can view data for all their linked children across multiple classes/sections |

---

## 3. Communication Integrity & Privacy

### 3.1 Teacher-to-Parent Direct Communication
When teachers need to discuss sensitive topics:
- Attendance problems or chronic absenteeism
- Behavioral issues or discipline matters
- Performance drops requiring parental intervention

If parents and students shared one account:
* The student could intercept, read, or delete notifications and messages before parents ever saw them.
* With separate accounts, messages addressed to `receiver_role: "parent"` go directly and privately to the parent's device.

### 3.2 Student-to-Teacher Academic Inquiries
* Students can message teachers directly with specific homework questions or academic doubts without cluttering their parents' inbox.

---

## 4. Database Schema Implementation in ParentBridge

In ParentBridge, this separation is implemented across three core tables:

### 1. `users` Table (Core Authentication)
Stores credentials and role identifiers:
* `user_id` (UUID, Primary Key)
* `email` (Unique)
* `password_hash`
* `role` (`'student'` or `'parent'`)

### 2. `students` Table (Academic Records)
Stores school-specific student information:
* `student_id` (UUID, Primary Key)
* `user_id` (References `users.user_id`, optional if student does not yet have a login)
* `full_name`
* `class_name` & `section`
* `roll_number` & `admission_number`
* `teacher_id` (Assigned mentor/teacher)

### 3. `student_parents` Table (Relational Junction)
Maps the relationship between parent user accounts and student academic records:
* `student_parent_id` (UUID, Primary Key)
* `student_id` (Foreign Key ➔ `students.student_id`)
* `parent_user_id` (Foreign Key ➔ `users.user_id`)
* `relationship` (e.g., `"Father"`, `"Mother"`, `"Guardian"`)
* **Constraint:** `UNIQUE(student_id, parent_user_id)` to prevent duplicate links.

---

## 5. API Endpoints Reflecting This Architecture

### Student Endpoints (`/student`)
Accessible by students to interact with their own curriculum:
- `GET /student/assignments` - View assignments for enrolled class
- `GET /student/grades` - View personal grades
- `GET /student/attendance` - View personal attendance
- `GET /student/progress` - View personal GPA and academic summary

### Parent Endpoints (`/parent`)
Accessible by parents to supervise their family:
- `GET /parent/children` - List all children linked to this parent
- `GET /parent/grades/{student_id}` - View specific child's report card
- `GET /parent/attendance/{student_id}` - View specific child's attendance record
- `GET /parent/progress/{student_id}` - View specific child's academic progress
- `GET /parent/teachers` - Contact information for teachers instructing their children
