# Course Catalog API

A backend for a course catalog built with FastAPI, SQLAlchemy, PostgreSQL, and Alembic. The API stores courses, students, and enrollments in a database. Database changes are managed through migrations.

## How to Run

Requirements: Python 3.11 or newer and PostgreSQL.

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root using `.env.example` as a template. Set the correct PostgreSQL connection details. Do not commit `.env`.

4. As the PostgreSQL `postgres` superuser, create the database:

   ```sql
   CREATE ROLE catalog_app LOGIN PASSWORD 'your-password';
   CREATE DATABASE course_catalog OWNER catalog_app;
   ```

   If the role already exists, only create the database if it does not exist.

5. From the project folder, create the database tables using migrations:

   ```powershell
   alembic upgrade head
   ```

6. Insert the initial data:

   ```powershell
   psql -h localhost -U catalog_app -d course_catalog -v ON_ERROR_STOP=1 -f seed.sql
   ```

7. Check the database and models:

   ```powershell
   alembic check
   python check_db.py
   python check_models.py
   ```

8. Start the API:

   ```powershell
   fastapi dev main.py
   ```

API documentation: http://127.0.0.1:8000/docs

## What Changed in the API

- Course data is now stored in PostgreSQL instead of a Python list. The data remains after restarting the server.
- `POST /students` creates a student and returns the generated student ID.
- `POST /enrollments` now uses `studentId` instead of `studentName`.
- `GET /enrollments` returns enrollment information together with course and student names.
- `GET /stats/courses` returns the number of enrollments for each course.
- `GET /courses` supports the `is_elective` and `level` filters, sorting, and pagination.
- `Course` now includes a required `level` field.
- Database constraint violations are converted into HTTP responses: duplicate records return 409, and missing referenced records return 404.

## Migrations

| Command | What it does |
|---|---|
| `alembic upgrade head` | Applies all missing migrations |
| `alembic downgrade -1` | Rolls back the last migration |
| `alembic current` | Shows the current database version |
| `alembic history` | Shows the migration history |
| `alembic revision --autogenerate -m "text"` | Generates a migration draft |
| `alembic check` | Checks for differences between models and database |
| `alembic upgrade 0001:0002 --sql` | Prints migration SQL without executing it |
| `alembic stamp head` | Marks the database as up to date without running migrations |

The project has two migrations:

- `0001_create_catalog_tables.py` creates the courses, students, and enrollments tables.
- `0002_add_course_level.py` adds the required course level column.

## Experiment Log

| Experiment | What I saw | Cause | How I fixed it |
|---|---|---|---|
| 1. Naming convention | Constraint names in the models did not match the database names. | The unique constraint naming template used only one column name. | Restored the template using `column_0_N_name`. |
| 2. Database validation | A short student name resulted in HTTP 500. | The Pydantic minimum-length validation had been removed, so the database constraint rejected the request. | Restored `Field(min_length=2)` in the schema. |
| 3. Constraint name typo | A duplicate email resulted in HTTP 500 instead of 409. | The error handler used a constraint name that did not match PostgreSQL's actual name. | Corrected the name in the error mapping. |
| 4. Model and database mismatch | `alembic check` detected changes to nullability and column type. | The database schema had been changed manually and no longer matched the models. | Restored `NOT NULL` and the original `text` type. |
| 5. Required column migration | Adding `level` as NOT NULL failed because existing courses had no value for it. | Existing rows need a value before a column can become required. | Added the column as nullable, filled existing rows, and then made it NOT NULL. |
| 6. Missing model import | Alembic proposed dropping the existing tables. | Without importing `models`, Alembic had empty metadata and could not see the tables. | Restored `import models` in `alembic/env.py`. |
| 7. Missing migration | `alembic check` detected an added `students.phone` column. | The model had changed but the database had no corresponding migration. | Removed the temporary model field and checked again. |
| 8. Multiple migration heads | `alembic upgrade head` reported multiple heads. | Two migrations had been created from the same parent revision. | Tested a merge migration, then removed the experimental files and restored the single `0002` head. |

## Decisions

**Why are database errors mapped by constraint name instead of SQLSTATE?**

Different constraints can have different meanings for the API even if they share an SQLSTATE. The constraint name lets the application identify the exact rule that was violated and return the appropriate HTTP response.

**Why catch the error after `commit()` instead of checking with SELECT first?**

A SELECT check can become outdated if another request inserts the same value before the current request commits. Letting the database enforce the constraint avoids this race condition.

**Why does migration 0002 use three steps?**

The existing courses need values before `level` can be required. The migration first adds a nullable column, fills existing rows, and then changes it to NOT NULL.

## Migration 0002 self-check

| What to check | Result |
|---|---|
| Goal and steps | Added the required `level` field using three steps: add nullable column, update existing rows, make it NOT NULL. |
| Data | Elective courses received `beginner`; other courses received `intermediate`. |
| Renames and drops | No renames or unrelated columns were removed. |
| Rollback | `alembic downgrade -1` successfully removed the `level` column. |
| Verification | `alembic upgrade head` succeeded and `alembic check` reported no new upgrade operations. |
| History | Migration 0002 follows 0001, and there is one head. |
| Application | The course response includes `level`, and the optional `level` filter works. |

## Final Checks

The following checks passed:

- `python check_db.py` connected to `course_catalog` as `catalog_app`.
- `python check_models.py` found no mismatches between the models and database.
- The database contained 6 courses, 3 students, and 6 enrollments.
- `alembic current` showed `0002 (head)`.
- `alembic check` reported `No new upgrade operations detected`.
- `python try_errors.py` printed `5 of 5 as expected`.
