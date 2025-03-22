-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Projeler tablosu
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Görevler tablosu
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    impact_score INTEGER NOT NULL CHECK (impact_score BETWEEN 1 AND 10),
    urgency_score INTEGER NOT NULL CHECK (urgency_score BETWEEN 1 AND 10),
    effort_score INTEGER NOT NULL CHECK (effort_score BETWEEN 1 AND 10),
    alignment_score INTEGER NOT NULL CHECK (alignment_score BETWEEN 1 AND 10),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    due_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Etiketler tablosu
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#3498db',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Görev ve etiket ilişkisi (many-to-many)
CREATE TABLE IF NOT EXISTS task_tags (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id),
    tag_id INTEGER REFERENCES tags(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(task_id, tag_id)
);

-- Aktivite günlüğü tablosu
CREATE TABLE IF NOT EXISTS activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Pareto analizleri için istatistikler tablosu
CREATE TABLE IF NOT EXISTS pareto_stats (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    analysis_date TIMESTAMP NOT NULL DEFAULT NOW(),
    top_tasks JSONB NOT NULL,
    total_tasks INTEGER NOT NULL,
    efficiency_score FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX IF NOT EXISTS idx_task_tags_tag_id ON task_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_pareto_stats_project_id ON pareto_stats(project_id);

-- Demo kullanıcı oluştur
INSERT INTO users (username, email, password_hash)
VALUES ('demo_user', 'demo@example.com', 'demo_password_hash')
ON CONFLICT (username) DO NOTHING;