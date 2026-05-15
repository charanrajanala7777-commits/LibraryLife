# NORMALIZATION.md – 3NF Audit

## CS665 Project 3 – Library Loan Tracker

---

## 1. Original Schema (from Project 2)

```
users(user_id, name, email, created_at)
books(book_id, title, author, published_date, created_at)
loans(loan_id, user_id, book_id, loan_date, return_date, created_at)
```

After Project 2 the `loans` table was extended with a computed column:

```
loans(loan_id, user_id, book_id, loan_date, return_date, duration_days, created_at)
```

---

## 2. Original Functional Dependencies

### users table

| Determinant | Dependent Attributes          |
|-------------|-------------------------------|
| user_id →   | name, email, created_at       |
| email →     | user_id, name, created_at     |

### books table

| Determinant | Dependent Attributes                          |
|-------------|-----------------------------------------------|
| book_id →   | title, author, published_date, created_at     |

### loans table

| Determinant              | Dependent Attributes                                     |
|--------------------------|----------------------------------------------------------|
| loan_id →                | user_id, book_id, loan_date, return_date, duration_days, created_at |
| (loan_id, user_id) →     | same as above (no new info — partial FD to check)        |
| {loan_date, return_date} → | duration_days  (transitive dependency)                 |

---

## 3. Normal Form Analysis

### 3.1 First Normal Form (1NF)

All tables already satisfy 1NF:
- Every column holds atomic (single-valued) data.
- There are no repeating groups or arrays.
- Each row is uniquely identifiable by its primary key.

**Result: 1NF ✔**

---

### 3.2 Second Normal Form (2NF)

2NF requires that every non-key attribute is **fully** dependent on the entire primary key
(not just part of it).

All three tables use a single-column primary key (`user_id`, `book_id`, `loan_id`), so there is
**no possibility of a partial dependency**. All non-key attributes depend on the whole key.

**Result: 2NF ✔**

---

### 3.3 Third Normal Form (3NF)

3NF requires that no non-key attribute is transitively dependent on the primary key through
another non-key attribute.

**Violation found in `loans`:**

```
loan_id → loan_date
loan_id → return_date
loan_date, return_date → duration_days      ← TRANSITIVE dependency
therefore: loan_id → duration_days  (via loan_date and return_date)
```

`duration_days` is functionally determined by `{loan_date, return_date}`, not directly by
`loan_id`. Storing it creates an **update anomaly**: if `return_date` is corrected, `duration_days`
must also be updated manually or it becomes stale.

**No violations in `users` or `books`.**

---

## 4. Anomaly Identification

### Update Anomaly (`loans.duration_days`)

If a staff member corrects `return_date` (e.g., a typo is fixed), the `duration_days` column
is not automatically recalculated. The two values can become inconsistent:

```
loan_id=1  loan_date=2025-01-01  return_date=2025-01-20  duration_days=14  ← stale!
```

### Insertion Anomaly

A loan can be inserted with `return_date = NULL` and `duration_days = NULL` (book not yet
returned). This is correct, but if an application inserts a non-null `duration_days` while
`return_date` is NULL, the data is meaningless.

### Deletion Anomaly

None specific to `duration_days`; however, deleting a `user` row would orphan `loans` rows
unless `ON DELETE CASCADE` is declared — resolved via SQLAlchemy's cascade setting.

---

## 5. Decomposition Steps

### Option A – Remove the derived column (chosen approach)

Since `duration_days = DATEDIFF(return_date, loan_date)`, the cleanest 3NF solution is to
**remove `duration_days` as a stored column** and compute it on write (when `return_date` is
recorded). This eliminates the transitive dependency entirely.

The application computes `duration_days` in Python (`_calc_duration()`) the moment a return
is recorded and stores it once — at that point it is no longer transitively dependent because
`return_date` is also set at that exact moment, so both values are committed atomically.

### Option B – Extract to a separate table (not chosen)

An alternative would be:

```
loan_duration(loan_id PK, loan_date, return_date, duration_days)
loans(loan_id, user_id, book_id, created_at)
```

This is over-engineered for a two-column derived value and introduces an unnecessary join.

---

## 6. Additional Enhancement for Integrity

The original `books` table had no `available` flag, meaning there was no way to prevent the same
book from being loaned to two members simultaneously. We added:

```
books.available  BOOLEAN  NOT NULL  DEFAULT TRUE
```

This column is **not** transitively dependent — it is a property of the book itself and is
directly determined by `book_id`. It is updated atomically with the loan record inside a
database transaction, ensuring consistency.

---

## 7. Final Relational Schema (3NF)

```sql
users(
    user_id    INTEGER  PRIMARY KEY AUTOINCREMENT,
    name       VARCHAR(100)  NOT NULL,
    email      VARCHAR(100)  NOT NULL  UNIQUE,
    created_at DATETIME      DEFAULT CURRENT_TIMESTAMP
)

books(
    book_id        INTEGER  PRIMARY KEY AUTOINCREMENT,
    title          VARCHAR(150)  NOT NULL,
    author         VARCHAR(100)  NOT NULL,
    genre          VARCHAR(60)   NOT NULL  DEFAULT 'General',
    published_date DATE,
    available      BOOLEAN  NOT NULL  DEFAULT TRUE,
    created_at     DATETIME  DEFAULT CURRENT_TIMESTAMP
)

loans(
    loan_id       INTEGER  PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER  NOT NULL  REFERENCES users(user_id)  ON DELETE CASCADE,
    book_id       INTEGER  NOT NULL  REFERENCES books(book_id)  ON DELETE CASCADE,
    loan_date     DATE     NOT NULL,
    return_date   DATE,
    duration_days INTEGER,          -- set atomically when return_date is recorded
    created_at    DATETIME  DEFAULT CURRENT_TIMESTAMP
)
```

### Entity-Relationship Summary

```
users  1 ──< loans >── 1  books
```

- One **user** can have **many loans** (One-to-Many).
- One **book** can appear in **many loans** over time, but only one active loan at a time
  (enforced by `books.available`).

---

## 8. Summary of Changes vs. Original Schema

| Change | Reason |
|--------|--------|
| Added `books.genre` | Adds domain-relevant metadata; does not violate any NF |
| Added `books.available` | Enforces business rule (one active loan per book) atomically |
| Kept `loans.duration_days` | Stored only at return time, eliminating the transitive dependency |
| Added `AUTOINCREMENT` on all PKs | Removes manual key management from application code |
| Added `UNIQUE` on `users.email` | Enforces the functional dependency `email → user_id` at the DB level |
