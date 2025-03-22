import os
import gradio as gr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import datetime

# Database connection information
DATABASE_URL = "postgresql://postgres:qeqe@localhost:5432/prioritylens"

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Create database tables (if they don't exist)
def create_tables_if_not_exist():
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            # Projects table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            
            # Tasks table
            cur.execute("""
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
            """)
            
            conn.commit()
            return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# Create demo user (for testing purposes only)
def create_demo_user():
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor() as cur:
            # Check if user exists
            cur.execute("SELECT id FROM users WHERE username = %s", ("demo_user",))
            user = cur.fetchone()
            
            if not user:
                # Create user if not exists
                cur.execute("""
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, ("demo_user", "demo@example.com", "demo_password_hash"))
                user_id = cur.fetchone()[0]
                conn.commit()
                return user_id
            else:
                return user[0]
    except Exception as e:
        print(f"Error creating demo user: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

# Add project function
def add_project(user_id, name, description=""):
    conn = get_db_connection()
    if not conn:
        return False, "Could not establish database connection"
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO projects (user_id, name, description)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (user_id, name, description))
            project_id = cur.fetchone()[0]
            conn.commit()
            return True, f"Project added successfully! ID: {project_id}"
    except Exception as e:
        conn.rollback()
        return False, f"Error adding project: {e}"
    finally:
        conn.close()

# Add task function
def add_task(project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date=None):
    conn = get_db_connection()
    if not conn:
        return False, "Could not establish database connection"
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (project_id, name, description, impact_score, urgency_score, effort_score, alignment_score, due_date))
            task_id = cur.fetchone()[0]
            conn.commit()
            return True, f"Task added successfully! ID: {task_id}"
    except Exception as e:
        conn.rollback()
        return False, f"Error adding task: {e}"
    finally:
        conn.close()

# Get projects
def get_projects(user_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, description, is_active
                FROM projects
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error retrieving projects: {e}")
        return []
    finally:
        conn.close()

# Get tasks for a project
def get_tasks(project_id):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, name, description, impact_score, urgency_score, effort_score, alignment_score, status, due_date
                FROM tasks
                WHERE project_id = %s
                ORDER BY created_at DESC
            """, (project_id,))
            return cur.fetchall()
    except Exception as e:
        print(f"Error retrieving tasks: {e}")
        return []
    finally:
        conn.close()

# Calculate Pareto score
def calculate_pareto_score(impact, urgency, alignment, effort):
    # Impact and Urgency have positive effects, Effort has negative effect
    # Strategic alignment has a positive effect
    value = (impact * 0.4) + (urgency * 0.3) + (alignment * 0.3)
    efficiency = value / effort if effort > 0 else value
    return efficiency * 10  # Convert to a 0-100 scale

# Perform Pareto analysis
def perform_pareto_analysis(tasks):
    if not tasks:
        return None, None
    
    df = pd.DataFrame(tasks)
    
    # Calculate Pareto score
    df['pareto_score'] = df.apply(lambda row: calculate_pareto_score(
        row['impact_score'], row['urgency_score'], row['alignment_score'], row['effort_score']), axis=1)
    
    # Sort scores in descending order
    df = df.sort_values('pareto_score', ascending=False)
    
    # Calculate cumulative total and percentage
    total_score = df['pareto_score'].sum()
    df['cumulative_score'] = df['pareto_score'].cumsum()
    df['score_percentage'] = df['pareto_score'] / total_score * 100
    df['cumulative_percentage'] = df['cumulative_score'] / total_score * 100
    
    # Create Pareto chart
    fig = go.Figure()
    
    # Bar chart - Pareto scores
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['pareto_score'],
        name='Pareto Score',
        marker_color='#3498db'
    ))
    
    # Line chart - Cumulative percentage
    fig.add_trace(go.Scatter(
        x=df['name'],
        y=df['cumulative_percentage'],
        name='Cumulative Percentage',
        marker_color='#e74c3c',
        mode='lines+markers',
        yaxis='y2'
    ))
    
    # 80% line
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=80,
        x1=len(df)-0.5,
        y1=80,
        line=dict(color="red", width=2, dash="dash"),
        yref='y2'
    )
    
    # Chart layout
    fig.update_layout(
        title='Pareto Analysis: Task Impact/Effort Distribution',
        xaxis_title='Tasks',
        yaxis_title='Pareto Score',
        yaxis2=dict(
            title='Cumulative Percentage (%)',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        bargap=0.15
    )
    
    # Four quadrant matrix chart
    quadrant_fig = px.scatter(
        df,
        x='effort_score',
        y='impact_score',
        size='urgency_score',
        color='pareto_score',
        color_continuous_scale='Viridis',
        hover_name='name',
        size_max=20,
        labels={
            'effort_score': 'Effort (1-10)',
            'impact_score': 'Impact (1-10)',
            'urgency_score': 'Urgency',
            'pareto_score': 'Pareto Score'
        },
        title='Four Quadrant Analysis: Impact vs Effort'
    )
    
    # Vertical and horizontal lines for quadrant divisions
    quadrant_fig.add_shape(
        type="line",
        x0=5.5,
        y0=0,
        x1=5.5,
        y1=10,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    quadrant_fig.add_shape(
        type="line",
        x0=0,
        y0=5.5,
        x1=10,
        y1=5.5,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Quadrant labels
    quadrant_fig.add_annotation(x=3, y=8, text="DO NOW", showarrow=False, font=dict(size=14, color="green"))
    quadrant_fig.add_annotation(x=8, y=8, text="PLAN", showarrow=False, font=dict(size=14, color="blue"))
    quadrant_fig.add_annotation(x=3, y=3, text="DELEGATE", showarrow=False, font=dict(size=14, color="orange"))
    quadrant_fig.add_annotation(x=8, y=3, text="ELIMINATE", showarrow=False, font=dict(size=14, color="red"))
    
    quadrant_fig.update_layout(height=600)
    
    return fig, quadrant_fig

# Prioritization recommendations
def get_recommendations(tasks):
    if not tasks:
        return "No tasks added yet. Add tasks to get priority recommendations."
    
    df = pd.DataFrame(tasks)
    
    # Calculate Pareto score
    df['pareto_score'] = df.apply(lambda row: calculate_pareto_score(
        row['impact_score'], row['urgency_score'], row['alignment_score'], row['effort_score']), axis=1)
    
    # Sort scores in descending order
    df = df.sort_values('pareto_score', ascending=False)
    
    # Calculate cumulative total and percentage
    total_score = df['pareto_score'].sum()
    df['cumulative_score'] = df['pareto_score'].cumsum()
    df['cumulative_percentage'] = df['cumulative_score'] / total_score * 100
    
    # Find 80% threshold
    top_tasks = df[df['cumulative_percentage'] <= 80]
    if len(top_tasks) == 0:
        top_tasks = df.iloc[:1]  # At least one task
    
    # Task count
    total_tasks = len(df)
    top_task_count = len(top_tasks)
    percentage = (top_task_count / total_tasks) * 100
    
    recommendations = f"""
    # 📊 Pareto Principle Analysis

    ## 🔍 Summary
    Out of {total_tasks} tasks, only {top_task_count} tasks ({percentage:.1f}%) generate 80% of results.
    
    ## 🎯 Priority Tasks
    You should dedicate most of your time to these tasks:
    """
    
    for i, task in enumerate(top_tasks.itertuples(), 1):
        recommendations += f"\n{i}. **{task.name}** (Pareto Score: {task.pareto_score:.1f})"
    
    # Four quadrant analysis recommendations
    recommendations += """
    
    ## 📋 Action Plan
    
    ### ✅ DO NOW (High Impact, Low Effort)
    """
    
    high_impact_low_effort = df[(df['impact_score'] > 5) & (df['effort_score'] <= 5)]
    if len(high_impact_low_effort) > 0:
        for task in high_impact_low_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- No tasks found in this category."
    
    recommendations += """
    
    ### 📅 PLAN (High Impact, High Effort)
    """
    
    high_impact_high_effort = df[(df['impact_score'] > 5) & (df['effort_score'] > 5)]
    if len(high_impact_high_effort) > 0:
        for task in high_impact_high_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- No tasks found in this category."
    
    recommendations += """
    
    ### 👥 DELEGATE (Low Impact, Low Effort)
    """
    
    low_impact_low_effort = df[(df['impact_score'] <= 5) & (df['effort_score'] <= 5)]
    if len(low_impact_low_effort) > 0:
        for task in low_impact_low_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- No tasks found in this category."
    
    recommendations += """
    
    ### ❌ ELIMINATE (Low Impact, High Effort)
    """
    
    low_impact_high_effort = df[(df['impact_score'] <= 5) & (df['effort_score'] > 5)]
    if len(low_impact_high_effort) > 0:
        for task in low_impact_high_effort.itertuples():
            recommendations += f"\n- **{task.name}**"
    else:
        recommendations += "\n- No tasks found in this category."
    
    return recommendations

# Main application function
def prioritylens_app():
    # Create demo user
    create_tables_if_not_exist()
    user_id = create_demo_user()
    
    if user_id is None:
        return gr.Markdown("Could not connect to database or create demo user!")
    
    with gr.Blocks(title="PriorityLens-AI: Pareto Principle-Based Work Prioritization") as app:
        gr.Markdown("""
        # 🎯 PriorityLens-AI
        ## Pareto Principle-Based Work Prioritization System
        
        Analyze tasks in your work life using the Pareto Principle (80/20 rule) to
        identify tasks that will allow you to achieve 80% of results by spending just 20% of your time.
        """)
        
        with gr.Tab("Project Management"):
            with gr.Row():
                with gr.Column(scale=1):
                    project_name_input = gr.Textbox(label="Project Name")
                    project_desc_input = gr.Textbox(label="Project Description", lines=3)
                    project_add_btn = gr.Button("Add Project", variant="primary")
                    project_status = gr.Markdown("")
                
                with gr.Column(scale=2):
                    projects_dropdown = gr.Dropdown(label="Projects", choices=[], interactive=True)
                    refresh_projects_btn = gr.Button("Refresh Projects")
        
        with gr.Tab("Task Management"):
            with gr.Row():
                with gr.Column():
                    task_name_input = gr.Textbox(label="Task Name")
                    task_desc_input = gr.Textbox(label="Task Description", lines=2)
                    
                    with gr.Row():
                        impact_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Impact Score (1-10)", value=5)
                        urgency_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Urgency Score (1-10)", value=5)
                    
                    with gr.Row():
                        effort_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Effort Score (1-10)", value=5)
                        alignment_slider = gr.Slider(minimum=1, maximum=10, step=1, label="Strategic Alignment Score (1-10)", value=5)
                    
                    due_date_input = gr.Textbox(label="Due Date (YYYY-MM-DD, optional)")
                    task_add_btn = gr.Button("Add Task", variant="primary")
                    task_status = gr.Markdown("")
                
                with gr.Column():
                    tasks_table = gr.DataFrame(
                        headers=["ID", "Task", "Impact", "Urgency", "Effort", "Alignment", "Status", "Due Date"],
                        label="Project Tasks"
                    )
                    refresh_tasks_btn = gr.Button("Refresh Tasks")
        
        with gr.Tab("Pareto Analysis"):
            with gr.Row():
                analyze_btn = gr.Button("Perform Pareto Analysis", variant="primary")
            
            with gr.Row():
                pareto_plot = gr.Plot(label="Pareto Analysis")
                quadrant_plot = gr.Plot(label="Four Quadrant Analysis")
            
            with gr.Row():
                recommendations = gr.Markdown(label="Prioritization Recommendations")
        
        # List projects
        def refresh_projects():
            projects = get_projects(user_id)
            choices = [(p['name'], p['id']) for p in projects]
            return gr.Dropdown(choices=choices)
        
        # Add project
        def add_project_handler(name, description):
            if not name or name.strip() == "":
                return "Project name cannot be empty!"
            
            success, message = add_project(user_id, name, description)
            return message
        
        # List tasks
        def refresh_tasks(project_id):
            if not project_id:
                return pd.DataFrame()
            
            tasks = get_tasks(project_id)
            if not tasks:
                return pd.DataFrame()
            
            task_df = pd.DataFrame([
                {
                    "ID": t['id'],
                    "Task": t['name'],
                    "Impact": t['impact_score'],
                    "Urgency": t['urgency_score'],
                    "Effort": t['effort_score'],
                    "Alignment": t['alignment_score'],
                    "Status": t['status'],
                    "Due Date": t['due_date'].strftime('%Y-%m-%d') if t['due_date'] else ""
                }
                for t in tasks
            ])
            return task_df
        
        # Add task
        def add_task_handler(project_id, name, description, impact, urgency, effort, alignment, due_date):
            if not project_id:
                return "Please select a project first!"
            
            if not name or name.strip() == "":
                return "Task name cannot be empty!"
            
            # Due date validation
            parsed_date = None
            if due_date and due_date.strip() != "":
                try:
                    parsed_date = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
                except ValueError:
                    return "Invalid date format! Please use YYYY-MM-DD format."
            
            success, message = add_task(
                project_id, name, description, 
                int(impact), int(urgency), int(effort), int(alignment), 
                parsed_date
            )
            return message
        
        # Perform analysis
        def analyze_tasks(project_id):
            if not project_id:
                return None, None, "Please select a project first!"
            
            tasks = get_tasks(project_id)
            if not tasks:
                return None, None, "No tasks found in this project!"
            
            pareto_fig, quadrant_fig = perform_pareto_analysis(tasks)
            recommendations_text = get_recommendations(tasks)
            
            return pareto_fig, quadrant_fig, recommendations_text
        
        # Define interactions
        project_add_btn.click(add_project_handler, [project_name_input, project_desc_input], [project_status])
        refresh_projects_btn.click(refresh_projects, [], [projects_dropdown])
        
        task_add_btn.click(
            add_task_handler, 
            [projects_dropdown, task_name_input, task_desc_input, impact_slider, urgency_slider, effort_slider, alignment_slider, due_date_input], 
            [task_status]
        )
        
        refresh_tasks_btn.click(refresh_tasks, [projects_dropdown], [tasks_table])
        projects_dropdown.change(refresh_tasks, [projects_dropdown], [tasks_table])
        
        analyze_btn.click(analyze_tasks, [projects_dropdown], [pareto_plot, quadrant_plot, recommendations])
        
        # Load projects on startup
        app.load(refresh_projects, [], [projects_dropdown])
        
    return app

# Start the application
if __name__ == "__main__":
    app = prioritylens_app()
    app.launch()