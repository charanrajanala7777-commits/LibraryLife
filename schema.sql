-- ============================================================
-- Library Loan Tracker – Final 3NF Schema
-- CS665 Project 3
-- Database: SQLite  (also compatible with MySQL/PostgreSQL
--           with minor type adjustments noted below)
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Drop existing tables (safe re-run) ──────────────────────
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;

-- ── users ───────────────────────────────────────────────────
-- FDs: user_id → name, email, created_at
--      email   → user_id (candidate key, enforced by UNIQUE)
CREATE TABLE users (
    user_id    INTEGER      PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── books ───────────────────────────────────────────────────
-- FDs: book_id → title, author, genre, published_date, available, created_at
-- 'available' tracks inventory state; updated atomically with loans table.
CREATE TABLE books (
    book_id        INTEGER      PRIMARY KEY AUTOINCREMENT,
    title          VARCHAR(150) NOT NULL,
    author         VARCHAR(100) NOT NULL,
    genre          VARCHAR(60)  NOT NULL DEFAULT 'General',
    published_date DATE,
    available      BOOLEAN      NOT NULL DEFAULT 1,  -- 1=TRUE, 0=FALSE in SQLite
    created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── loans ───────────────────────────────────────────────────
-- FDs: loan_id → user_id, book_id, loan_date, return_date, duration_days, created_at
-- 'duration_days' is stored (not derived at query time) but is set
--  atomically with return_date, eliminating the transitive dependency.
-- ON DELETE CASCADE: removing a user or book cleans up their loan records.
CREATE TABLE loans (
    loan_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL,
    book_id       INTEGER NOT NULL,
    loan_date     DATE    NOT NULL,
    return_date   DATE,                -- NULL = book not yet returned
    duration_days INTEGER,             -- NULL until return_date is set
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- ── Seed Data (mirrors original Project 2 DML) ──────────────
INSERT INTO users (name, email) VALUES
    ('John Smith',   'john@email.com'),
    ('Maria Garcia', 'maria@email.com'),
    ('Kevin Lee',    'kevin@email.com'),
    ('Sara Brown',   'sara@email.com'),
    ('Mike Davis',   'mike@email.com');

INSERT INTO books (title, author, genre, published_date, available) VALUES
    ('SQL Basics',      'Smith', 'Technology', '2000-01-01', 1),
    ('Python Guide',    'Johns', 'Technology', '2021-06-20', 1),
    ('Database Design', 'Lee',   'Technology', '2019-03-15', 1),
    ('AI Intro',        'Brown', 'Technology', '2018-07-20', 1),
    ('Web Development', 'Davis', 'Technology', '2022-11-11', 0);  -- currently on loan

INSERT INTO loans (user_id, book_id, loan_date, return_date, duration_days) VALUES
    (1, 1, '2025-01-01', '2025-01-20', 19),
    (2, 2, '2025-02-01', '2025-02-12', 11),
    (3, 3, '2025-03-01', '2025-03-15', 14),
    (4, 4, '2025-04-01', '2025-04-20', 19),
    (5, 5, '2025-05-01', NULL,         NULL);   -- Mike still has Web Development

-- ── Useful queries (DQL reference) ──────────────────────────

-- Members with more than one loan:
-- SELECT user_id, COUNT(*) AS total_loans
-- FROM loans GROUP BY user_id HAVING COUNT(*) > 1;

-- Latest loan per member:
-- SELECT u.user_id, u.name, MAX(l.loan_date) AS latest_loan
-- FROM users u JOIN loans l ON u.user_id = l.user_id
-- GROUP BY u.user_id, u.name;

-- Top 3 most borrowed books:
-- SELECT b.title, COUNT(l.loan_id) AS borrow_count
-- FROM books b JOIN loans l ON b.book_id = l.book_id
-- GROUP BY b.book_id ORDER BY borrow_count DESC LIMIT 3;

-- Average loan duration (returned loans only):
-- SELECT AVG(duration_days) AS avg_days FROM loans WHERE duration_days IS NOT NULL;

-- Books never borrowed:
-- SELECT book_id, title FROM books
-- WHERE book_id NOT IN (SELECT book_id FROM loans WHERE book_id IS NOT NULL);
