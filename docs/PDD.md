# Process Definition Document (PDD)

## Employee Attendance & Report Automation

**Document status:** Business-process baseline for Phase 2 design  
**Process owner:** Human Resources  
**Automation platform:** UiPath (planned for Phase 2)

## Process overview

The process collects daily employee attendance, validates each record, stores it centrally, and prepares attendance information for HR reporting. Phase 1 supplies a web application and API that represent the source system to be automated in Phase 2.

## Business objective

Reduce repetitive attendance consolidation, improve data accuracy, provide a traceable processing log, and deliver reports to HR more quickly.

## Current manual process

1. HR receives attendance data from supervisors in spreadsheets or emails.
2. An HR employee checks employee IDs, dates, statuses, and working times.
3. The employee enters or corrects records in the attendance application.
4. HR exports or copies the data into an Excel report.
5. The report is reviewed and distributed to stakeholders.
6. Errors are corrected manually and the report is regenerated.

The process is repetitive and is vulnerable to missing rows, invalid statuses, inconsistent time formats, and transcription errors.

## Proposed automated process

1. A UiPath robot reads configuration and the input attendance file.
2. It validates required columns and basic data formats.
3. The robot logs into the attendance web application using credentials stored securely outside the workflow.
4. It enters new or updated attendance records through the web form.
5. It retrieves consolidated JSON or XML attendance data.
6. It creates an Excel summary and an exception report.
7. It writes operational logs and saves outputs to configured folders.
8. It reports completion or exceptions to the operator.

## Inputs

- CSV or Excel attendance file
- Employee ID and employee name
- Attendance date
- Status: Present, Absent, or Leave
- Check-in and check-out times for Present records
- Application URL and robot credentials from configuration

## Outputs

- Records stored in the attendance database
- Consolidated attendance data from JSON or XML API
- Planned Excel attendance report
- Planned exception report for rejected rows
- Application and robot execution logs

## Business rules

- Employee ID, employee name, date, and status are mandatory.
- Status must be Present, Absent, or Leave.
- Dates use `YYYY-MM-DD`; times use 24-hour `HH:MM` format.
- Present records require a check-in time.
- Absent and Leave records must not contain working times.
- Check-out time cannot be earlier than check-in time.
- Employee ID plus date uniquely identifies a record; resubmission updates it.
- Invalid rows must be logged and must not stop other valid rows from being processed.

## Applications involved

- Employee Attendance Flask web application
- UiPath Studio/Robot (Phase 2)
- Microsoft Excel or CSV files
- PostgreSQL in a shared environment, or SQLite for local development
- File system for reports and logs

## Exception scenarios

| Scenario | Expected handling |
|---|---|
| Input file is missing or locked | Log a system exception and stop safely |
| Required column or value is missing | Record a business exception and continue with the next row |
| Status, date, or time is invalid | Record the validation message in the exception report |
| Login fails | Retry according to configuration, then stop and notify the operator |
| API is unavailable or times out | Retry a limited number of times; log failure if unavailable |
| Duplicate employee/date record | Update the existing record according to the business rule |
| Database or report write fails | Log a system exception and preserve available diagnostic details |

Credentials and sensitive values must never be written to logs.

## Assumptions

- Input files use an agreed column layout.
- Employee IDs are supplied by HR and are considered valid identifiers.
- The application and database are available during the scheduled run.
- The robot has permission to access required input and output folders.
- A human operator reviews exception records.
- Email distribution and production scheduling are outside the current Phase 2 design scope.
- UiPath workflows will be implemented and validated later on a Windows machine.

## Expected benefits

- Less manual data entry and consolidation
- Fewer formatting and transcription errors
- Faster report preparation
- Consistent application of attendance rules
- Audit-friendly logs and exception records
- A reusable integration through JSON and XML services
