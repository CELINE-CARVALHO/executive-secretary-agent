PRAGMA foreign_keys = ON;

-- =====================
-- USERS
-- =====================
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('executive', 'admin')) DEFAULT 'executive',
    gmail_token TEXT,
    calendar_token TEXT,
    preferences TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- =====================
-- EMAILS
-- =====================
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gmail_message_id TEXT UNIQUE NOT NULL,
    thread_id TEXT,
    sender TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    received_at TIMESTAMP NOT NULL,
    processed_at TIMESTAMP,
    processing_status TEXT CHECK (
        processing_status IN ('pending', 'processed', 'failed')
    ) DEFAULT 'pending',
    ai_summary TEXT,
    urgency_level TEXT CHECK (urgency_level IN ('low', 'medium', 'high')),
    category TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =====================
-- TASKS
-- =====================
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    estimated_duration INTEGER,
    suggested_deadline TIMESTAMP,
    actual_deadline TIMESTAMP,
    status TEXT CHECK (
        status IN ('pending_approval', 'approved', 'scheduled', 'completed', 'rejected')
    ) DEFAULT 'pending_approval',
    completion_percentage INTEGER DEFAULT 0,
    created_by_agent BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =====================
-- APPROVALS
-- =====================
CREATE TABLE approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    approval_type TEXT CHECK (
        approval_type IN ('task_creation', 'calendar_scheduling', 'email_response')
    ),
    status TEXT CHECK (
        status IN ('pending', 'approved', 'rejected', 'modified')
    ) DEFAULT 'pending',
    original_data TEXT,
    modified_data TEXT,
    user_feedback TEXT,
    decision_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- =====================
-- CALENDAR EVENTS
-- =====================
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER,
    user_id INTEGER NOT NULL,
    google_event_id TEXT UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    location TEXT,
    attendees TEXT,
    reminder_minutes INTEGER DEFAULT 15,
    created_by_agent BOOLEAN DEFAULT 1,
    sync_status TEXT CHECK (
        sync_status IN ('pending', 'synced', 'failed')
    ) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =====================
-- NOTIFICATIONS
-- =====================
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_id INTEGER,
    notification_type TEXT CHECK (
        notification_type IN ('reminder', 'follow_up', 'daily_summary', 'approval_request')
    ),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    status TEXT CHECK (
        status IN ('pending', 'sent', 'failed')
    ) DEFAULT 'pending',
    delivery_method TEXT CHECK (
        delivery_method IN ('email', 'in_app')
    ) DEFAULT 'email',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- =====================
-- AI LOGS
-- =====================
CREATE TABLE ai_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    agent_name TEXT NOT NULL,
    input_data TEXT NOT NULL,
    output_data TEXT,
    prompt_used TEXT,
    model_used TEXT DEFAULT 'llama-3.3-70b-versatile',
    tokens_used INTEGER,
    latency_ms INTEGER,
    confidence_score REAL,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- =====================
-- API LOGS
-- =====================
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    request_body TEXT,
    response_status INTEGER,
    response_body TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
