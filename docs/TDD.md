# Technical Design Document (TDD)

## Employee Attendance & Report Automation

**Status:** Phase 1 application implemented and tested; Phase 2 UiPath design only.  
**Important:** UiPath workflows have not been built or executed. Implementation requires UiPath Studio on Windows.

## Solution overview

Phase 1 is a Flask attendance application with browser pages, JSON REST endpoints, an XML endpoint, validation, logging, and SQLAlchemy persistence to SQLite or PostgreSQL. Phase 2 will add a UiPath robot that reads CSV transactions and enters valid attendance through the browser. Separate REST and XML workflows will demonstrate service integration and reconciliation without replacing the primary UI automation.

## Architecture

```text
Attendance CSV + non-secret configuration
                    |
                    v
              UiPath Robot
              /     |     \
             v      v      v
       Flask UI   REST API  XML endpoint
             \      |      /
              v     v     v
            Flask service layer
                    |
             SQLite/PostgreSQL
                    |
                    v
          Results CSV + robot logs
```

## Components

| Component | Status | Responsibility |
|---|---|---|
| Flask routes and templates | Implemented | Login, dashboard, form, JSON API, and XML API |
| Service and model layers | Implemented | Validation, create/update logic, queries, persistence, and serialization |
| Python logging and pytest | Implemented | Application diagnostics and automated Phase 1 tests |
| `automation/input` | Prepared | Controlled Phase 2 transaction input, including one invalid test row |
| `automation/config/config.json` | Prepared | Non-secret URLs, username, and file paths |
| `Main.xaml` | Design only | Orchestration, input/output, counts, lifecycle, and reconciliation |
| `Login.xaml` | Design only | Secure login and dashboard verification |
| `ProcessAttendanceRow.xaml` | Design only | Validation, browser form entry, and result verification |
| `API_Workflow.xaml` | Design only | JSON GET/count demonstration and possible future POST approach |
| `XML_Workflow.xaml` | Design only | XML request, parsing, extraction, and count |

The Markdown specifications under `automation/uipath-specs` are build instructions, not executable workflows.

## UiPath architecture and workflow components

`Main.xaml` will use a simple sequential transaction loop appropriate for this portfolio scope. It loads configuration, reads the CSV into a `DataTable`, opens one browser session, logs in, and invokes `ProcessAttendanceRow.xaml` for every row. Row-level `Try Catch` separates business exceptions from system exceptions. After processing, it writes a result CSV, invokes or optionally runs the API/XML checks, logs reconciled counts, and closes the browser in `Finally`.

Reusable workflows use explicit `in_` and `out_` arguments with narrow scopes. The complete activity-level design is in:

- [`Main_Workflow.md`](../automation/uipath-specs/Main_Workflow.md)
- [`Login_Workflow.md`](../automation/uipath-specs/Login_Workflow.md)
- [`Process_Attendance_Workflow.md`](../automation/uipath-specs/Process_Attendance_Workflow.md)
- [`API_Workflow.md`](../automation/uipath-specs/API_Workflow.md)
- [`XML_Workflow.md`](../automation/uipath-specs/XML_Workflow.md)
- [`Exception_Handling.md`](../automation/uipath-specs/Exception_Handling.md)
- [`Variables.md`](../automation/uipath-specs/Variables.md)

## Input and output

Input is `automation/input/employee_attendance.csv`, with employee ID, employee name, date, status, check-in time, and check-out time. EMP106 is intentionally invalid because `Remote` is not an allowed status.

The planned output is `automation/output/automation_results.csv` with one outcome per source row: `SUCCESS`, `BUSINESS_EXCEPTION`, or `SYSTEM_EXCEPTION`. It includes error type/message and processing timestamp. Output count must equal input count. A non-generated format example is stored in `automation/samples`.

## Browser automation

The robot will use Chrome or Edge through **Use Application/Browser**. It logs in once and processes rows through the Add/Update form using **Click**, **Type Into**, **Select Item**, and **Check App State**. Submission is successful only when the dashboard success alert is detected; a completed Click alone is not adequate verification.

Employee ID plus date is the application’s unique business key, so resubmitting that pair updates the record. UI automation remains the principal Phase 2 path to demonstrate browser skills. The API POST option is documented only as an alternative/future comparison.

## Selectors

Selectors should prioritize stable semantic attributes already present in Phase 1, including input IDs (`username`, `password`, `employee_id`, `employee_name`, `date`, `status`, `check_in_time`, `check_out_time`) and durable visible headings/button text. Avoid element indexes, screen coordinates, CSS colors, and position-based selectors. Inspect and validate each selector with UI Explorer in the chosen Windows browser and test it at multiple window sizes.

## Configuration

`automation/config/config.json` contains the application URL, username, input/output paths, and service endpoints. It contains no password. Resolve repository-relative paths with `Path.Combine` on Windows. Future environment-dependent settings should include timeouts, retry count, credential asset name, browser choice, and screenshot/log path.

Phase 1 continues to use `DATABASE_URL`, `BOT_USERNAME`, `BOT_PASSWORD`, and `SECRET_KEY` environment variables. The configured UiPath username must match the running Flask environment.

## Credentials

Retrieve the password at runtime as `SecureString` from a UiPath Orchestrator Credential Asset. Windows Credential Manager is acceptable for local Windows development. Do not place passwords in `config.json`, workflow arguments stored as plain strings, XAML, logs, screenshots, or Git. The local Flask default is for development demonstrations only.

## Logging

Flask writes rotating logs to `logs/app.log`. The robot should use UiPath **Log Message** with run ID, workflow/activity, employee ID when available, category, and sanitized message. Use Information for milestones and successes, Warning for business exceptions/recovered transients, and Error for system/fatal failures. Log a final reconciliation summary without credentials or full payloads.

## Business exceptions

Invalid transaction data—missing employee ID, invalid status/date/time, missing Present check-in, times on Absent/Leave, or reversed times—should throw `UiPath.Core.BusinessRuleException`. Record the rejected row, increment the business exception count, and continue without retrying unchanged data.

## System exceptions

Technical failures include unavailable browser/application/file/credential, selector failure, API timeout, malformed service response, and output failure. Use `Try Catch`, screenshots for appropriate UI failures, limited retry for transient operations, and `Finally` for cleanup. Continue after a row failure only if the browser returns to a verified known state. Initialization and output failures are fatal.

## REST API integration

The planned API workflow calls `GET /api/attendance`, checks HTTP 200, deserializes JSON to a `JObject`, reads and validates the record count, and logs it. A later POST workflow may submit validated JSON and interpret 201/200 responses, but it will not replace UI automation in this phase.

## XML processing

The planned XML workflow calls `GET /api/attendance/xml`, checks HTTP 200, uses **Deserialize XML**, verifies the `attendance_records` root, extracts `attendance` elements, and logs their count. Network errors, non-success status codes, malformed XML, and schema mismatches are system exceptions. Controlled malformed content or a mock should be used for negative testing.

## Testing strategy

- Keep the existing pytest service and Flask endpoint regression suite passing.
- Build and debug one UiPath workflow at a time on Windows, beginning with login and one valid Present row.
- Execute valid Present, Absent, and Leave cases and data-validation negatives.
- Test browser/application unavailability, login failure, and selector recovery.
- Test JSON success/failure and XML success/malformed content separately.
- Execute an end-to-end controlled CSV run and reconcile input count against all three result counts.
- Retain sanitized results, logs, and useful screenshots as evidence; record package versions and Windows/browser versions.
- Use [`TEST_CASES.md`](TEST_CASES.md) as the acceptance checklist.

UiPath execution results must not be reported until the workflows are assembled and actually run in UiPath Studio/Robot on Windows.
