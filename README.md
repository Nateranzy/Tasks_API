# Task API

A REST API with JWT authentication built with FastAPI, SQLAlchemy and SQLite. Each user creates and manages only their own tasks.

## Features

- User registration with hashed passwords (Argon2)
- Login with a JWT access token (valid for 30 minutes)
- Task CRUD protected by login
- User isolation: another user's task returns 404
- Status filter and pagination on the task list
- 17 automated tests with pytest
- Interactive documentation at `/docs`

## Tech stack

| Technology | Purpose |
|------------|---------|
| FastAPI | API framework |
| SQLAlchemy 2 + SQLite | Database |
| PyJWT | Login tokens |
| pwdlib (Argon2) | Password hashing |
| Pydantic | Data validation |
| pytest | Automated tests |

## Endpoints

| Method | Route | Description | Login required |
|--------|-------|-------------|----------------|
| POST | `/auth/register` | Creates a user | No |
| POST | `/auth/login` | Returns the JWT token | No |
| POST | `/tarefas` | Creates a task | Yes |
| GET | `/tarefas` | Lists the user's tasks (`concluida`, `limite`, `pular`) | Yes |
| GET | `/tarefas/{id}` | Shows one task | Yes |
| PATCH | `/tarefas/{id}` | Updates title, description or status | Yes |
| DELETE | `/tarefas/{id}` | Deletes a task | Yes |

The `/tarefas` routes and their query parameters keep Portuguese names (`tarefas` = tasks, `concluida` = completed, `limite` = limit, `pular` = skip).

## Getting started (Windows, PowerShell)

```powershell
git clone https://github.com/Nateranzy/api-tarefas.git
cd api-tarefas
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the `.env` file with a random secret key:

```powershell
"SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" | Set-Content .env -Encoding ascii
```

Start the server:

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`, click **Authorize** with the email and password of a registered user, and try the task routes.

## Running the tests

```powershell
python -m pytest -v
```

The tests use an in-memory database and never touch `tarefas.db`.

## Project structure

```
app/
├── main.py          # creates the API and registers the routes
├── config.py        # reads SECRET_KEY from .env
├── database.py      # database connection
├── models.py        # User and Task tables
├── schemas.py       # shape of incoming and outgoing data
├── security.py      # password hashing and JWT tokens
├── deps.py          # requires login on protected routes
└── routers/
    ├── auth.py      # registration and login
    └── tarefas.py   # task CRUD
tests/               # automated tests
```

## Security decisions

- Passwords are never stored in plain text, only as Argon2 hashes.
- Login returns the same message for an unknown email and a wrong password, and verifies a dummy hash so the response time is similar in both cases.
- The secret key lives in `.env`, which is not committed to the repository.
- The owner of each task comes from the token, never from a field sent by the client.
- Other users' tasks return 404, without revealing that they exist.

## Next steps

- Database migrations with Alembic
- Docker
- PostgreSQL
- Deployment