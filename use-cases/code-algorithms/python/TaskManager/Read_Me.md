🗂️ Task Manager CLI

A Python-based command-line Task Manager that supports task creation, prioritization, tagging, due dates, parsing from natural text, conflict resolution, and advanced task scoring.

✨ Features
Create and manage tasks via CLI
Priority levels (Low, Medium, High, Urgent)
Task statuses (Todo, In Progress, Review, Done)
Due dates with overdue detection
Tagging system for organization
Natural language task parsing
Task scoring and intelligent prioritization
Merge system for local/remote task synchronization
Persistent storage using JSON
Full unit test coverage


📁 Project Structure

task_manager/
│
├── models.py              # Task, enums, and core data model
├── storage.py             # JSON persistence layer
├── task_manager.py        # Business logic layer
├── cli.py                 # Command-line interface
├── task_parser.py        # Natural language parsing
├── task_priority.py      # Scoring & sorting logic
├── task_list_merge.py    # Sync/merge logic
│
├── tests/
│   ├── test_task_parser.py
│   ├── test_task_priority.py
│   ├── test_task_list_merge.py
│
└── tasks.json            # Persistent storage file (auto-generated)


🚀 Getting Started
1. Clone the repository
git clone <your-repo-url>
cd task_manager
2. Run the CLI
python cli.py

Or:

python -m task_manager.cli
🛠️ CLI Usage
Create a task
python cli.py create "Buy milk" -p 2 -d 2026-04-20 -t shopping,errands
List tasks
python cli.py list
python cli.py list --status todo
python cli.py list --priority 3
python cli.py list --overdue
Update task status
python cli.py status <task_id> done
Update priority
python cli.py priority <task_id> 4
Update due date
python cli.py due <task_id> 2026-05-01
Add / remove tags
python cli.py tag <task_id> urgent
python cli.py untag <task_id> urgent
View task details
python cli.py show <task_id>
Delete task
python cli.py delete <task_id>
View statistics
python cli.py stats
🧠 Natural Language Task Parsing

You can create tasks using smart text input:

Examples
Buy milk @shopping !2 #tomorrow
Finish report @work !urgent #friday
Call client @sales !high #next_week
Syntax
@tag → adds a tag
!1–4 → sets priority
!urgent | !high | !medium | !low → named priority
#today | #tomorrow | #friday | #YYYY-MM-DD → due date


📊 Task Scoring System

Tasks are automatically ranked based on:

Priority level
Due date proximity
Status (done/review penalties)
Tags (critical, blocker, urgent)
Recent updates

This allows intelligent task sorting and prioritization.

🔄 Task Synchronization

The system supports merging two task sources:

Local vs remote conflict resolution
Latest update wins (with exceptions)
Completed tasks take priority
Tags are merged (union strategy)
Automatic update propagation tracking
🧪 Running Tests

Run all unit tests:

python -m unittest discover

Or run specific tests:

python -m unittest tests.test_task_parser
python -m unittest tests.test_task_priority
python -m unittest tests.test_task_list_merge


💾 Data Storage

Tasks are stored in:

tasks.json

Features:

Automatic saving on changes
JSON serialization with datetime support
Recovery-safe loading


⚙️ Requirements
Python 3.8+
Standard library only (no external dependencies)

👨‍💻 Author

Built as a learning project for:

Object-Oriented Programming
CLI design
Testing with unittest
System design fundamentals