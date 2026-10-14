# Course Catalog API

A backend for a course catalog built with FastAPI and Pydantic. It provides endpoints for retrieving courses, filtering and sorting results, and pagination.

## How to Run

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the development server:

   ```bash
   fastapi dev main.py
   ```

4. Open the interactive API documentation at `http://127.0.0.1:8000/docs`.

## What Was Verified

- `GET /` — returns a message confirming that the API is running.
- `GET /courses` — returns all six courses, sorted by popularity by default.
- `GET /courses/web-security` — returns the Web Security Essentials course.
- `GET /courses/nope` — returns HTTP 404 when the course does not exist.
- `GET /courses?is_elective=true` — returns two elective courses.
- `GET /courses?is_elective=false` — returns four required courses.
- `GET /courses?sort=title` — sorts courses alphabetically by title.
- `GET /courses?page=1&page_size=2` — returns the first two courses.
- `GET /courses?page=2&page_size=2` — returns the second page of courses.
- `GET /courses?page=3&page_size=2` — returns the third page of courses.
- `GET /courses?page=4&page_size=2` — returns an empty list.