# Exception Handling Design

**Status:** Phase 2 design for future Windows implementation.

## Classification

### Business exceptions

Business exceptions mean the applications are working but a transaction violates an attendance rule. Throw `UiPath.Core.BusinessRuleException` after validation and before UI entry.

Examples include missing employee ID/name/date/status, invalid status, invalid date/time, Present without check-in, times provided for Absent/Leave, and check-out earlier than check-in.

At the row level:

1. Catch `BusinessRuleException` before the general exception Catch.
2. Add a `BUSINESS_EXCEPTION` output row with the sanitized validation message.
3. Increment `businessExceptionCount` and log a Warning with employee ID when available.
4. Do not retry unchanged bad data.
5. Continue with the next input row.

### System exceptions

System exceptions mean the technology or environment prevented processing. Examples include browser unavailable, selector failure, application unavailable, API timeout, file unavailable/locked, credential retrieval failure, and output write failure.

At the row level, catch `System.Exception`, add a `SYSTEM_EXCEPTION` result, increment `systemExceptionCount`, and continue only if the application is returned to a known usable state. Initialization failures—configuration, input file, credential, login, or browser startup—are fatal because processing cannot begin. Output-write failure is also fatal because results would not be auditable.

## Try Catch structure

```text
Top-level Try
  Initialize, read input, open browser, login
  For Each Row
    Row Try
      Validate
      Submit and verify
      Record SUCCESS
    Catch BusinessRuleException
      Record BUSINESS_EXCEPTION; continue
    Catch Exception
      Screenshot; record SYSTEM_EXCEPTION; recover or stop
  Write results and reconcile
Top-level Catch Exception
  Log fatal failure; attempt to preserve current results
Finally
  Close browser and release resources
```

Use **Throw** for a new exception and **Rethrow** inside a Catch to preserve the original stack trace. Catch specific exceptions before `System.Exception`.

## Logging

Use **Log Message** with consistent fields: run ID, workflow, employee ID where available, category, activity, and sanitized message. Use Information for start/success/summary, Warning for business exceptions and recovered transients, and Error for system/fatal exceptions. Never log passwords, `SecureString` values, or complete attendance payloads.

## Screenshots

Use **Take Screenshot** on UI-related system failures, save under a Git-ignored output/log folder, and name files with run ID, employee ID, and UTC timestamp. Capture only the application window when possible. Do not capture password entry or other sensitive screens. A screenshot failure must not hide the original exception.

## Retry and recovery

- Use a small, configurable retry count only for transient navigation, API calls, or UI-element loading.
- Add delay/backoff between retries and log each attempt.
- Do not retry business exceptions.
- Do not blindly retry `Save attendance`; verify whether the record was already saved first.
- After a row-level selector failure, attempt to navigate back to the dashboard and verify it. If recovery fails, rethrow to stop the run.
- Always close resources in `Finally`.

## Results and reconciliation

Every input row must produce exactly one result. At completion verify:

`successCount + businessExceptionCount + systemExceptionCount = attendanceData.Rows.Count`

A mismatch is a system/reconciliation failure and should mark the run unsuccessful even if individual rows were entered.
