Here's the English translation of the PriorityLens-AI project description:

# PriorityLens-AI
## Pareto Principle-Based Work Prioritization System

PriorityLens-AI is an application that analyzes tasks in your work life using the Pareto Principle (80/20 rule) and helps you identify tasks that will allow you to achieve 80% of results by spending just 20% of your time.

## Features

* **Pareto Analysis**: Determines which tasks have the highest impact
* **Four-Quadrant Analysis**: Classifies tasks based on impact and effort dimensions:
   * High Impact / Low Effort (DO NOW)
   * High Impact / High Effort (PLAN)
   * Low Impact / Low Effort (DELEGATE)
   * Low Impact / High Effort (ELIMINATE)
* **PostgreSQL Database**: Stores your data securely and scalably
* **Visualizations**: Interactive charts to understand your work priorities
* **Project and Task Organization**: Organize your work projects and tasks

## Installation

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

## Usage

1. Create a new project from the **Project Management** tab.
2. In the **Task Management** tab:
   * Add tasks
   * Define impact, urgency, effort, and strategic alignment scores for each task
3. In the **Pareto Analysis** tab:
   * Click the "Perform Pareto Analysis" button
   * View results and examine prioritization recommendations

## Technical Structure

* **Backend**: Python + Gradio
* **Database**: PostgreSQL
* **Analysis**: Pandas, NumPy, Plotly

## Advanced Developments

* Multi-User Support
* ML Model Integration
* API Integration (Trello, Asana, Jira)
* Calendar Synchronization
* Mobile Application

## Contributing

To contribute to the project, please send a pull request or open an issue for problems.

## License

MIT