# 📚 Library Loan Tracker

A full-stack web application for managing a public library's members, book catalogue, and loan
records. Built with Python/Flask, SQLite, SQLAlchemy, and Bootstrap 5 as part of CS665 Project 3.

---

## Project Description

The **Library Loan Tracker** lets library staff:

- Manage **members** (add, edit, delete)
- Manage the **book catalogue** (add, edit, delete, track availability)
- Record **loans** — issuing a book to a member and logging the return date
- View a **summary dashboard** with aggregate statistics (total members, books, active loans,
  average loan duration, monthly activity, top borrowed titles)

The application enforces data integrity through server-side validation, database-level constraints
(unique email, foreign keys), and SQLAlchemy transactions.

---

## Tech Stack

| Layer      | Technology                                  |
|------------|---------------------------------------------|
| Language   | Python 3.10+                                |
| Backend    | Flask 3.x                                   |
| ORM        | Flask-SQLAlchemy (SQLAlchemy 2.x)           |
| Database   | SQLite (file: `instance/library.db`)        |
| Frontend   | HTML5, CSS3, Bootstrap 5.3, Jinja2          |
| Version Control | Git                                    |

---

## Installation Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd library_app
```

### 2. Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

The application uses SQLite. The schema is automatically created on first run via SQLAlchemy's
`db.create_all()`.  A seed function populates five members, five books, and five sample loans
(mirroring the original project SQL data) on the first startup.

If you prefer to initialise via the provided SQL script instead:

```bash
# SQLite CLI
sqlite3 instance/library.db < schema.sql
```

> **Note:** The SQL script (`schema.sql`) reflects the final 3NF schema described in
> `NORMALIZATION.md`.

---

## Usage

### Run the development server

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

### Main features

| URL              | Description                              |
|------------------|------------------------------------------|
| `/`              | Summary dashboard with KPIs              |
| `/users`         | List / add / edit / delete members       |
| `/users/<id>/loans` | All loans for a specific member       |
| `/books`         | List / add / edit / delete books         |
| `/loans`         | List all loans, return a book            |
| `/loans/add`     | Issue a new loan (transactional)         |

---

## Running Step-by-Step (from scratch)

```bash
# 1. Clone
git clone <your-repo-url>
cd library_app

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server (creates & seeds DB automatically)
python app.py

# 5. Open browser
# http://127.0.0.1:5000
```

---

## Project Structure

```
library_app/
├── app.py                  # Flask application + models + routes
├── requirements.txt        # Python dependencies
├── schema.sql              # 3NF SQL schema (DDL only)
├── .gitignore
├── README.md
├── NORMALIZATION.md        # Part I: 3NF audit
├── AI_LOG.md               # Generative AI disclosure
├── static/
│   └── css/
│       └── style.css
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── users.html
    ├── user_form.html
    ├── user_loans.html
    ├── books.html
    ├── book_form.html
    ├── loans.html
    └── loan_form.html
```

---

## Git Commit Workflow (example)

```bash
git init
git add .gitignore
git commit -m "chore: initial repo setup with .gitignore"

git add app.py requirements.txt
git commit -m "feat: add Flask app with SQLAlchemy models (User, Book, Loan)"

git add templates/ static/
git commit -m "feat: add Jinja2 templates and Bootstrap styling"

git add NORMALIZATION.md schema.sql
git commit -m "docs: add 3NF normalization report and SQL schema"

git add README.md AI_LOG.md
git commit -m "docs: add README and AI disclosure log"
```
