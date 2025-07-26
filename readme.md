# Kanban Board Backend

This is a simple Django REST API backend for a Kanban board project.

## 📦 Features

- Create and manage boards
- Create, update, and delete tasks (tickets)
- Add comments to tasks
- Role-based permissions for users
- Authentication required for all actions

## ▶️ Getting Started

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/kanban-backend.git
cd kanban-backend


2. Create and activate a virtual environment

bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

3. Install the dependencies

bash

pip install -r requirements.txt

4. Run migrations

bash

python manage.py migrate

5. Start the development server

bash

python manage.py runserver


⚠️ Notes
This is the backend only – the frontend is in a separate repository.

Do not upload your .env or db.sqlite3 file to GitHub.

All actions require an authenticated user.