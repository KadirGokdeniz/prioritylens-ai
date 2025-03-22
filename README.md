# PriorityLens-AI

## Pareto Principle-Based Work Prioritization System

PriorityLens-AI is a sophisticated task management application that leverages the Pareto Principle (80/20 rule) to transform how you prioritize work. By analyzing your tasks through multiple dimensions including impact, urgency, effort, and strategic alignment, it identifies the vital few tasks that will deliver maximum results with minimal time investment.

<table>
  <tr>
    <td><img src="./images/1.png" alt="Project Management Interface" width="100%"></td>
    <td><img src="./images/2.png" alt="Task Management Interface" width="100%"></td>
  </tr>
  <tr>
    <td><em>Project Management Interface - Creating New Projects in PriorityLens-AI</em></td>
    <td><em>Task Management Interface - Adding and Scoring Tasks with Impact, Urgency, Effort, and Alignment Metrics</em></td>
  </tr>
  <tr>
    <td><img src="./images/3.png" alt="Pareto Analysis Dashboard" width="100%"></td>
    <td><img src="./images/4.png" alt="Prioritization Recommendations" width="100%"></td>
  </tr>
  <tr>
    <td><em>Pareto Analysis Dashboard - Task Impact/Effort Distribution and Four Quadrant Prioritization Matrix</em></td>
    <td><em>Prioritization Recommendations - Pareto Principle Analysis Results and Action Plan Categories</em></td>
  </tr>
</table>
## The Power of the Pareto Principle in Your Workflow

The Pareto Principle, discovered by economist Vilfredo Pareto, suggests that approximately 80% of outcomes result from just 20% of causes. PriorityLens-AI applies this powerful concept to your daily work:

- **Focus on What Matters**: Identify the critical 20% of tasks that will deliver 80% of your results
- **Data-Driven Decisions**: Replace gut feelings with quantitative analysis of task importance
- **Visual Decision Making**: See your priorities mapped on intuitive quadrant charts
- **Efficiency Optimization**: Maximize your productivity by allocating time to high-impact activities

## Key Features

### 📊 Comprehensive Pareto Analysis

The system calculates a unique "Pareto Score" for each task based on:
- Impact (1-10): How significant the results will be
- Urgency (1-10): Time sensitivity of the task
- Effort (1-10): Resources and time required
- Strategic Alignment (1-10): How well it aligns with your goals

This multi-dimensional analysis identifies which tasks deserve your immediate attention and which can be delegated or eliminated.

### 🧩 Four-Quadrant Prioritization Matrix

Tasks are automatically classified into action categories:

| | |
|---|---|
| **HIGH IMPACT / LOW EFFORT**<br>✅ DO NOW<br>*Maximum return with minimal investment* | **HIGH IMPACT / HIGH EFFORT**<br>📅 PLAN<br>*Strategic priorities that need scheduling* |
| **LOW IMPACT / LOW EFFORT**<br>👥 DELEGATE<br>*Quick wins that can be assigned to others* | **LOW IMPACT / HIGH EFFORT**<br>❌ ELIMINATE<br>*Resource drains with minimal value* |

### 📈 Interactive Data Visualizations

The system generates dynamic visualizations powered by Plotly:
- Pareto charts showing cumulative impact of prioritized tasks
- Quadrant scatter plots mapping tasks by effort and impact
- Task distribution analytics by project and priority

### 🗃️ Advanced Project Organization

- Create and manage multiple projects
- Track tasks across various stages
- Generate detailed reports on productivity patterns
- Analyze historical data to improve future planning

## Technical Architecture

### Gradio-Powered User Interface

PriorityLens-AI uses Gradio to provide an intuitive, responsive interface that:
- Requires zero frontend development knowledge
- Delivers a clean, professional UI with minimal code
- Provides interactive components for task scoring and analysis
- Enables real-time visualization updates as you add and modify tasks
- Offers a seamless experience across devices without complex web development

### PostgreSQL Database Integration

The application leverages PostgreSQL's enterprise-grade database capabilities:

- **Relational Data Structure**: Sophisticated relationships between tasks, projects, users, and analytics
- **Transactional Integrity**: Ensures your priority data is never corrupted
- **Advanced Indexing**: Fast retrieval of task data even with thousands of entries
- **JSON Capabilities**: Stores complex analysis results in flexible formats
- **Scalability**: Grows with your needs from personal use to team collaboration

### Data Science Backend

Built with Python's powerful data science stack:
- **Pandas**: For efficient data manipulation and analysis
- **NumPy**: For advanced mathematical operations
- **Plotly**: For interactive, publication-quality visualizations

## Installation Guide

### 1. PostgreSQL Database Setup

```bash
# PostgreSQL installation (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Database creation
sudo -u postgres psql
CREATE DATABASE prioritylens;
CREATE USER prioritylens_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE prioritylens TO prioritylens_user;
\q

# Loading database schema
psql -U prioritylens_user -d prioritylens -f schema.sql
```

For Windows users, install PostgreSQL from the official website and use pgAdmin or the command line tools.

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application

```bash
# Set database URL
export DATABASE_URL="postgresql://prioritylens_user:your_password@localhost:5432/prioritylens"
# Windows PowerShell:
# $env:DATABASE_URL="postgresql://prioritylens_user:your_password@localhost:5432/prioritylens"

# Run the application
python app.py
```

The application will be available at http://127.0.0.1:7860 in your browser.

## Usage Guide

### 1. Project Management

Start by creating projects that group related tasks:
- Define project scope and objectives
- Set project timelines and contexts
- Track progress across multiple initiatives

### 2. Task Management

For each project, create tasks with detailed attributes:
- Assign impact scores (1-10) based on business value
- Set urgency scores (1-10) for time sensitivity
- Estimate effort scores (1-10) for resource requirements
- Rate strategic alignment (1-10) with organizational goals
- Add descriptions and deadlines

### 3. Priority Analysis

Leverage the power of Pareto analysis:
- Generate priority visualizations with a single click
- View the critical 20% of tasks that will deliver 80% of results
- Explore the quadrant distribution of your workload
- Receive AI-enhanced recommendations for task scheduling
- Export reports for team discussions and planning sessions

## Future Development Roadmap

PriorityLens-AI will continue to evolve with planned features:

- **Multi-User Collaboration**: Team-based priority management
- **Machine Learning Integration**: Predictive task prioritization
- **API Integrations**: Connect with Trello, Asana, Jira, and other tools
- **Calendar Synchronization**: Automatically schedule high-priority tasks
- **Mobile Applications**: iOS and Android versions for on-the-go priority management

## Contributing

We welcome contributions to enhance PriorityLens-AI:
- Fork the repository
- Create a feature branch
- Submit a pull request with your improvements
- Open issues for bugs or feature requests

## License

Released under the MIT License, allowing for both personal and commercial use with proper attribution.

---

*Transform your productivity with PriorityLens-AI — because not all tasks are created equal.*
