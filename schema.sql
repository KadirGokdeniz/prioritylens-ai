-- PostgreSQL database schema for PriorityLens-AI

-- Create projects table
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    impact_score INTEGER CHECK (impact_score BETWEEN 1 AND 10),
    urgency_score INTEGER CHECK (urgency_score BETWEEN 1 AND 10),
    effort_score INTEGER CHECK (effort_score BETWEEN 1 AND 10),
    alignment_score INTEGER CHECK (alignment_score BETWEEN 1 AND 10),
    status VARCHAR(50) DEFAULT 'Pending',
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Diğer tablolar...