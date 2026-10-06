# Employee Attendance & Report Automation

A portfolio project demonstrating the foundation for an employee attendance RPA solution. Phase 1 provides a small Flask application, database persistence, CSV processing, REST/XML services, validation, logging, tests, and process documentation. Phase 2 currently provides implementation-ready UiPath specifications and controlled test artifacts.

## Architecture

```text
Browser / future UiPath robot
          |
   Flask routes and APIs
          |
 Validation and service layer
          |
 SQLAlchemy data model
          |
 SQLite (local) / PostgreSQL
```

The application automatically loads the sample CSV the first time an empty database starts. A record is uniquely identified by `employee_id` and `date`, so a second submission updates the existing record.

## Technology stack

- Python 3 and Flask
- SQLAlchemy with SQLite or PostgreSQL
- HTML, CSS, and small vanilla JavaScript
- JSON REST API and XML web service
- CSV sample input
- pytest
- Python rotating-file logging

## Project structure

```text
app/          Flask application, services, model, templates, and CSS
automation/   Phase 2 input, config, samples, output location, and UiPath specifications
data/         Sample attendance CSV
docs/         PDD and starter TDD
logs/         Runtime application logs (ignored by Git)
tests/        Unit and API tests
config.py     Environment-based application configuration
run.py        Development entry point
```

## Setup

Python 3.10 or later is recommended.

```bash
cd employee-attendance-rpa
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set development credentials and a session key. The shown values are examples:

```bash
export BOT_USERNAME=attendance_bot
export BOT_PASSWORD=choose-a-development-password
export SECRET_KEY=choose-a-random-development-key
```

If the variables are omitted, documented development defaults are used. Do not use those defaults outside local demonstrations.

SQLite is the default and requires no setup. To use PostgreSQL:

```bash
export DATABASE_URL='postgresql+psycopg://username:password@localhost/attendance_db'
```

Create the PostgreSQL database first; tables are created when the application starts.

## Run

```bash
python run.py
```

Open <http://127.0.0.1:5000>. Log in with the configured bot credentials. The dashboard displays records and the **Add / Update** page saves attendance.

## API examples

List JSON attendance:

```bash
curl http://127.0.0.1:5000/api/attendance
```

Create or update a record:

```bash
curl -X POST http://127.0.0.1:5000/api/attendance \
  -H 'Content-Type: application/json' \
  -d '{"employee_id":"EMP008","employee_name":"Neha Das","date":"2026-10-06","status":"Present","check_in_time":"09:00","check_out_time":"17:30"}'
```

Retrieve XML attendance:

```bash
curl http://127.0.0.1:5000/api/attendance/xml
```

API status codes include `201` for creation, `200` for update/read, `400` for validation errors, `415` for a non-JSON POST, and `500` for a database error.

## Test

```bash
pytest -v
```

Tests use an isolated in-memory SQLite database. They cover business validation, create/update behavior, login protection, API error responses, and JSON/XML output.

## Logging

Runtime events are written to `logs/app.log`. Log files and local databases are excluded from Git. Important successful operations, invalid requests, failed logins, and unexpected database errors are recorded.

## Process documentation

- [Process Definition Document](docs/PDD.md)
- [Technical Design Document](docs/TDD.md)
- [Test Cases](docs/TEST_CASES.md)
- [UiPath Phase 2 notes](automation/README.md)

## RPA Automation Architecture

```text
CSV
 |
 v
UiPath Robot
 |
 +------> Flask Web UI
 |
 +------> REST API
 |
 +------> XML Endpoint
 |
 v
Automation Results / Logs
```

The planned robot uses the web UI as its primary transaction path so the portfolio demonstrates browser automation, stable selectors, form entry, dropdown selection, and result verification. JSON and XML workflows provide separate service-integration demonstrations.

**UiPath workflow implementation requires UiPath Studio on Windows and is currently represented by detailed workflow specifications.** No XAML workflows have been created and no UiPath execution has been tested in the current macOS environment.

The design package includes:

- A ten-row [automation input CSV](automation/input/employee_attendance.csv), with EMP106 intentionally invalid
- A non-secret [configuration file](automation/config/config.json)
- An [expected results sample](automation/samples/expected_automation_results.csv)
- Beginner-reproducible [workflow specifications](automation/uipath-specs/Main_Workflow.md)
- Business/system exception guidance and a complete test catalogue

The password is intentionally absent from configuration. The future Windows implementation must retrieve it as a `SecureString` from a UiPath Orchestrator Credential Asset or an appropriate local credential store.

## Future UiPath implementation

On Windows, the workflows will be assembled from the specifications, selectors will be captured and validated in Chrome or Edge, secure credentials will be connected, and the controlled test cases will be executed. The robot will read attendance from CSV, log into the site, submit valid records through the web form, process JSON/XML results, generate a result report, and distinguish business from system exceptions.

Potential later improvements include UiPath Orchestrator assets and queues, scheduled execution, email delivery, report reconciliation, and automated end-to-end robot tests.

## SDLC and version-control approach

The PDD captures business requirements and exceptions; the TDD translates them into components, workflows, and tests. Work can be organized into short Agile iterations: Phase 1 application, Phase 2 robot, Phase 3 reporting and hardening. Use feature branches and focused commits, review test results before merging, and avoid committing credentials, logs, virtual environments, or local databases.
