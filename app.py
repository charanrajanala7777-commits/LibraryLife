"""
CS665 Project 3 - Library Life
Full-stack Flask application using SQLite + SQLAlchemy.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cs665-library-secret-2025")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///library.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ─────────────────────────────────────────────
# Models  (3NF schema)
# ─────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"
    user_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship("Loan", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.name}>"


class Book(db.Model):
    __tablename__ = "books"
    book_id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title          = db.Column(db.String(150), nullable=False)
    author         = db.Column(db.String(100), nullable=False)
    genre          = db.Column(db.String(60), nullable=False, default="General")
    published_date = db.Column(db.Date, nullable=True)
    available      = db.Column(db.Boolean, nullable=False, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    loans = db.relationship("Loan", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Book {self.title}>"


class Loan(db.Model):
    __tablename__ = "loans"
    loan_id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id       = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    book_id       = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    loan_date     = db.Column(db.Date, nullable=False, default=date.today)
    return_date   = db.Column(db.Date, nullable=True)
    duration_days = db.Column(db.Integer, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="loans")
    book = db.relationship("Book", back_populates="loans")

    def __repr__(self):
        return f"<Loan {self.loan_id}>"


# ─────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────

def _calc_duration(loan_date, return_date):
    if loan_date and return_date:
        return (return_date - loan_date).days
    return None


# ─────────────────────────────────────────────
# Routes – Dashboard
# ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    total_users  = db.session.query(db.func.count(User.user_id)).scalar()
    total_books  = db.session.query(db.func.count(Book.book_id)).scalar()
    total_loans  = db.session.query(db.func.count(Loan.loan_id)).scalar()
    active_loans = db.session.query(db.func.count(Loan.loan_id)).filter(Loan.return_date == None).scalar()
    avg_duration = db.session.query(db.func.avg(Loan.duration_days)).filter(Loan.duration_days != None).scalar()
    avg_duration = round(avg_duration, 1) if avg_duration else 0

    # Top 3 most borrowed books
    top_books = (
        db.session.query(Book.title, db.func.count(Loan.loan_id).label("borrow_count"))
        .join(Loan, Book.book_id == Loan.book_id)
        .group_by(Book.book_id)
        .order_by(db.desc("borrow_count"))
        .limit(3)
        .all()
    )

    # Loans per month
    loans_by_month = (
        db.session.query(
            db.func.strftime("%Y-%m", Loan.loan_date).label("month"),
            db.func.count(Loan.loan_id).label("cnt"),
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_books=total_books,
        total_loans=total_loans,
        active_loans=active_loans,
        avg_duration=avg_duration,
        top_books=top_books,
        loans_by_month=loans_by_month,
    )


# ─────────────────────────────────────────────
# Routes – Users
# ─────────────────────────────────────────────

@app.route("/users")
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users.html", users=users)


@app.route("/users/add", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        # Server-side validation
        if not name:
            flash("Name is required.", "danger")
            return render_template("user_form.html", action="Add", user=None)
        if not email or "@" not in email:
            flash("A valid email address is required.", "danger")
            return render_template("user_form.html", action="Add", user=None)
        if User.query.filter_by(email=email).first():
            flash("That email is already registered.", "warning")
            return render_template("user_form.html", action="Add", user=None)

        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash(f"User '{name}' added successfully!", "success")
        return redirect(url_for("list_users"))

    return render_template("user_form.html", action="Add", user=None)


@app.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name:
            flash("Name is required.", "danger")
            return render_template("user_form.html", action="Edit", user=user)
        if not email or "@" not in email:
            flash("A valid email address is required.", "danger")
            return render_template("user_form.html", action="Edit", user=user)
        existing = User.query.filter_by(email=email).first()
        if existing and existing.user_id != user_id:
            flash("That email is already in use by another account.", "warning")
            return render_template("user_form.html", action="Edit", user=user)

        user.name  = name
        user.email = email
        db.session.commit()
        flash("User updated.", "success")
        return redirect(url_for("list_users"))

    return render_template("user_form.html", action="Edit", user=user)


@app.route("/users/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.name}' and all their loans have been removed.", "info")
    return redirect(url_for("list_users"))


@app.route("/users/<int:user_id>/loans")
def user_loans(user_id):
    user  = User.query.get_or_404(user_id)
    loans = Loan.query.filter_by(user_id=user_id).order_by(Loan.loan_date.desc()).all()
    return render_template("user_loans.html", user=user, loans=loans)


# ─────────────────────────────────────────────
# Routes – Books
# ─────────────────────────────────────────────

@app.route("/books")
def list_books():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template("books.html", books=books)


@app.route("/books/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title          = request.form.get("title", "").strip()
        author         = request.form.get("author", "").strip()
        genre          = request.form.get("genre", "General").strip()
        published_date = request.form.get("published_date", "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("book_form.html", action="Add", book=None)
        if not author:
            flash("Author is required.", "danger")
            return render_template("book_form.html", action="Add", book=None)
        if not genre:
            flash("Genre is required.", "danger")
            return render_template("book_form.html", action="Add", book=None)

        pub_date = None
        if published_date:
            try:
                pub_date = date.fromisoformat(published_date)
                if pub_date > date.today():
                    flash("Published date cannot be in the future.", "danger")
                    return render_template("book_form.html", action="Add", book=None)
            except ValueError:
                flash("Invalid date format. Use YYYY-MM-DD.", "danger")
                return render_template("book_form.html", action="Add", book=None)

        new_book = Book(title=title, author=author, genre=genre, published_date=pub_date)
        db.session.add(new_book)
        db.session.commit()
        flash(f"Book '{title}' added successfully!", "success")
        return redirect(url_for("list_books"))

    return render_template("book_form.html", action="Add", book=None)


@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == "POST":
        title          = request.form.get("title", "").strip()
        author         = request.form.get("author", "").strip()
        genre          = request.form.get("genre", "General").strip()
        published_date = request.form.get("published_date", "").strip()

        if not title:
            flash("Title is required.", "danger")
            return render_template("book_form.html", action="Edit", book=book)
        if not author:
            flash("Author is required.", "danger")
            return render_template("book_form.html", action="Edit", book=book)

        pub_date = book.published_date
        if published_date:
            try:
                pub_date = date.fromisoformat(published_date)
                if pub_date > date.today():
                    flash("Published date cannot be in the future.", "danger")
                    return render_template("book_form.html", action="Edit", book=book)
            except ValueError:
                flash("Invalid date format. Use YYYY-MM-DD.", "danger")
                return render_template("book_form.html", action="Edit", book=book)

        book.title          = title
        book.author         = author
        book.genre          = genre
        book.published_date = pub_date
        db.session.commit()
        flash("Book updated.", "success")
        return redirect(url_for("list_books"))

    return render_template("book_form.html", action="Edit", book=book)


@app.route("/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f"Book '{book.title}' removed.", "info")
    return redirect(url_for("list_books"))


# ─────────────────────────────────────────────
# Routes – Loans  (includes TRANSACTION logic)
# ─────────────────────────────────────────────

@app.route("/loans")
def list_loans():
    loans = (
        Loan.query
        .join(User)
        .join(Book)
        .order_by(Loan.loan_date.desc())
        .all()
    )
    return render_template("loans.html", loans=loans, today=date.today().isoformat())


@app.route("/loans/add", methods=["GET", "POST"])
def add_loan():
    users = User.query.order_by(User.name).all()
    books = Book.query.filter_by(available=True).order_by(Book.title).all()

    if request.method == "POST":
        user_id_str = request.form.get("user_id", "").strip()
        book_id_str = request.form.get("book_id", "").strip()
        loan_date_str = request.form.get("loan_date", "").strip()

        # Validation
        if not user_id_str or not book_id_str:
            flash("Both a member and a book must be selected.", "danger")
            return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())
        if not loan_date_str:
            flash("Loan date is required.", "danger")
            return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())

        try:
            user_id   = int(user_id_str)
            book_id   = int(book_id_str)
            loan_date = date.fromisoformat(loan_date_str)
        except ValueError:
            flash("Invalid input values.", "danger")
            return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())

        if loan_date > date.today():
            flash("Loan date cannot be in the future.", "danger")
            return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())

        book = Book.query.get_or_404(book_id)
        if not book.available:
            flash("That book is already on loan.", "warning")
            return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())

        # ── TRANSACTION: create loan + mark book unavailable atomically ──
        try:
            new_loan = Loan(user_id=user_id, book_id=book_id, loan_date=loan_date)
            db.session.add(new_loan)
            book.available = False          # inventory update
            db.session.commit()             # single commit = atomic
            flash("Loan recorded and book marked as unavailable.", "success")
        except Exception as exc:
            db.session.rollback()
            flash(f"Transaction failed: {exc}", "danger")

        return redirect(url_for("list_loans"))

    return render_template("loan_form.html", users=users, books=books, loan=None, today=date.today().isoformat())


@app.route("/loans/return/<int:loan_id>", methods=["POST"])
def return_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    return_date_str = request.form.get("return_date", "").strip()

    if not return_date_str:
        flash("Return date is required.", "danger")
        return redirect(url_for("list_loans"))

    try:
        return_date = date.fromisoformat(return_date_str)
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("list_loans"))

    if return_date < loan.loan_date:
        flash("Return date cannot be before loan date.", "danger")
        return redirect(url_for("list_loans"))

    # ── TRANSACTION: update loan + restore book availability atomically ──
    try:
        loan.return_date   = return_date
        loan.duration_days = _calc_duration(loan.loan_date, return_date)
        loan.book.available = True
        db.session.commit()
        flash(f"Book returned. Loan duration: {loan.duration_days} day(s).", "success")
    except Exception as exc:
        db.session.rollback()
        flash(f"Transaction failed: {exc}", "danger")

    return redirect(url_for("list_loans"))


@app.route("/loans/delete/<int:loan_id>", methods=["POST"])
def delete_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    # Restore availability if not yet returned
    if loan.return_date is None:
        loan.book.available = True
    db.session.delete(loan)
    db.session.commit()
    flash("Loan record deleted.", "info")
    return redirect(url_for("list_loans"))


# ─────────────────────────────────────────────
# DB init + seed
# ─────────────────────────────────────────────

def seed_data():
    if User.query.count() > 0:
        return  # already seeded

    users = [
        User(name="John Smith",  email="john@email.com"),
        User(name="Maria Garcia", email="maria@email.com"),
        User(name="Kevin Lee",   email="kevin@email.com"),
        User(name="Sara Brown",  email="sara@email.com"),
        User(name="Mike Davis",  email="mike@email.com"),
    ]
    db.session.add_all(users)
    db.session.flush()

    books = [
        Book(title="SQL Basics",        author="Smith",  genre="Technology",  published_date=date(2000, 1, 1)),
        Book(title="Python Guide",       author="Johns",  genre="Technology",  published_date=date(2021, 6, 20)),
        Book(title="Database Design",    author="Lee",    genre="Technology",  published_date=date(2019, 3, 15)),
        Book(title="AI Intro",           author="Brown",  genre="Technology",  published_date=date(2018, 7, 20)),
        Book(title="Web Development",    author="Davis",  genre="Technology",  published_date=date(2022, 11, 11)),
    ]
    db.session.add_all(books)
    db.session.flush()

    loans = [
        Loan(user_id=users[0].user_id, book_id=books[0].book_id,
             loan_date=date(2025, 1, 1),  return_date=date(2025, 1, 20),  duration_days=19),
        Loan(user_id=users[1].user_id, book_id=books[1].book_id,
             loan_date=date(2025, 2, 1),  return_date=date(2025, 2, 12),  duration_days=11),
        Loan(user_id=users[2].user_id, book_id=books[2].book_id,
             loan_date=date(2025, 3, 1),  return_date=date(2025, 3, 15),  duration_days=14),
        Loan(user_id=users[3].user_id, book_id=books[3].book_id,
             loan_date=date(2025, 4, 1),  return_date=date(2025, 4, 20),  duration_days=19),
        Loan(user_id=users[4].user_id, book_id=books[4].book_id,
             loan_date=date(2025, 5, 1),  return_date=None,               duration_days=None),
    ]
    db.session.add_all(loans)

    # Sync availability: last book still on loan
    books[4].available = False

    db.session.commit()
    print("✔  Seed data inserted.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, port=5000)
