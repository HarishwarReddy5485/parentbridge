-- ==============================================================================
-- PARENTBRIDGE - SUPABASE POSTGRESQL SCHEMA
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. Create User Role Enum
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM (
        'admin',
        'class_teacher',
        'teacher',
        'student',
        'parent'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Users Table (Core Auth & Profile)
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT,
    role user_role NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Admins Table
CREATE TABLE IF NOT EXISTS admins (
    admin_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    employee_id TEXT UNIQUE,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    is_super_admin BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Class Teachers Table
CREATE TABLE IF NOT EXISTS class_teachers (
    class_teacher_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    employee_id TEXT UNIQUE,
    assigned_class TEXT,
    assigned_section TEXT,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. Teachers Table (Subject Teachers)
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    employee_id TEXT UNIQUE,
    qualification TEXT,
    specialization TEXT,
    subjects TEXT[] NOT NULL DEFAULT '{}',
    classes TEXT[] NOT NULL DEFAULT '{}',
    joining_date DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE REFERENCES users(user_id) ON DELETE SET NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    date_of_birth DATE,
    gender TEXT,
    class_name TEXT NOT NULL,
    section TEXT,
    father_name TEXT,
    mother_name TEXT,
    roll_number TEXT,
    admission_number TEXT UNIQUE,
    admission_date DATE,
    address TEXT,
    city TEXT,
    state TEXT,
    teacher_id UUID REFERENCES teachers(teacher_id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 7. Student Parents Table (Parent-Child Junction)
CREATE TABLE IF NOT EXISTS student_parents (
    student_parent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    parent_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    relationship TEXT DEFAULT 'Parent',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, parent_user_id)
);

-- 8. Assignments Table
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    subject TEXT NOT NULL,
    description TEXT,
    class_name TEXT NOT NULL,
    section TEXT,
    assigned_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    total_marks NUMERIC(10,2) NOT NULL DEFAULT 100.00,
    attachment_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 9. Grades Table
CREATE TABLE IF NOT EXISTS grades (
    grade_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    exam_type TEXT NOT NULL,
    marks_obtained NUMERIC(10,2) NOT NULL,
    total_marks NUMERIC(10,2) NOT NULL,
    grade TEXT,
    remarks TEXT,
    exam_date DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 10. Attendance Table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    teacher_id UUID NOT NULL REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('present', 'absent', 'late', 'leave')),
    remarks TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(student_id, date)
);

-- 11. Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    sender_role user_role NOT NULL,
    receiver_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_role user_role NOT NULL,
    student_id UUID REFERENCES students(student_id) ON DELETE SET NULL,
    subject TEXT,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 12. Notices Table
CREATE TABLE IF NOT EXISTS notices (
    notice_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_by UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    target_role user_role,
    target_class_name TEXT,
    target_section TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_students_class_sec ON students(class_name, section);
CREATE INDEX IF NOT EXISTS idx_students_teacher_id ON students(teacher_id);
CREATE INDEX IF NOT EXISTS idx_assignments_class ON assignments(class_name, section);
CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX IF NOT EXISTS idx_messages_sender_receiver ON messages(sender_id, receiver_id);
CREATE INDEX IF NOT EXISTS idx_notices_target ON notices(target_role, target_class_name);
