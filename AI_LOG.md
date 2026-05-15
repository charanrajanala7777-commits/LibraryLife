# AI_LOG.md – Generative AI Disclosure

## CS665 Project 3 – Library Loan Tracker

All AI assistance used during this project is documented below per course policy.

---

## Entry 1

**Tool:** Claude (Anthropic)

**Prompt:**
> "Generate a Flask route that handles creating a loan record and simultaneously marks the book
> as unavailable, wrapped in a transaction so both changes succeed or both fail."

**AI Output Summary:**
The AI produced a Flask route using `db.session.add()`, setting `book.available = False`, and
calling `db.session.commit()` inside a `try/except` block with `db.session.rollback()` on error.

**My Modification:**
I adapted the route to use my specific model names (`Loan`, `Book`) and column names
(`book.available`). I added server-side validation (checking `book.available` before creating
the loan, validating the loan date is not in the future, ensuring the user and book IDs are
valid integers). I also split the "return" action into its own route (`/loans/return/<id>`) to
keep concerns separate, which the AI had combined into one route.

---

## Entry 2

**Tool:** Claude (Anthropic)

**Prompt:**
> "Write a NORMALIZATION.md that documents original functional dependencies, update/insert/delete
> anomalies, and decomposition steps for a schema with tables: users, books, loans."

**AI Output Summary:**
The AI produced a Markdown document outlining 1NF → 2NF → 3NF analysis and identified the
transitive dependency `loan_id → duration_days` (via `loan_date` and `return_date`).

**My Modification:**
I verified the analysis against my actual schema. I chose Option A (remove derived column and
recompute at write time) over the AI's suggested Option B (separate table), because the separate
table was unnecessary complexity for a two-column computation. I added the `books.available`
enhancement section, which the AI did not include.

---

## Entry 3

**Tool:** Claude (Anthropic)

**Prompt:**
> "Create a Bootstrap 5 Jinja2 base template for a Flask library app with a navbar, flash
> message support, and a footer."

**AI Output Summary:**
The AI generated a base HTML template with Bootstrap CDN links, a `navbar-dark bg-primary`
navbar, and a flash messages block.

**My Modification:**
I changed the navbar links to use Flask's `url_for()` function and added active-state detection
using `request.endpoint`. I added Bootstrap Icons CDN and replaced generic icon placeholders
with specific `bi-` icon classes. I also added the custom `style.css` link and adjusted the
container structure to match my application's page layout.

---

## Entry 4

**Tool:** Claude (Anthropic)

**Prompt:**
> "Write a schema.sql file for SQLite that reflects the 3NF library schema with users, books,
> and loans tables including foreign keys and cascade deletes."

**AI Output Summary:**
The AI produced CREATE TABLE statements with standard SQLite syntax.

**My Modification:**
I added the `available` column to `books` (which the AI omitted), added the `genre` column,
changed all primary keys to `INTEGER PRIMARY KEY AUTOINCREMENT` (SQLite-idiomatic), and verified
that the SQLAlchemy model definitions in `app.py` matched the SQL exactly. I also added the seed
`INSERT` statements sourced from the original Project 2 DML data.
