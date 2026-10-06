# Process Attendance Workflow Specification

**Planned file:** `ProcessAttendanceRow.xaml`  
**Status:** Design only; implementation requires UiPath Studio on Windows.

## Purpose and arguments

Validate one CSV `DataRow`, enter it through the Flask web form, and verify the success message. The browser is already open and logged in.

| Direction | Name | Type | Purpose |
|---|---|---|---|
| In | `in_AttendanceRow` | `System.Data.DataRow` | Current CSV transaction |
| Out | `out_SubmissionSuccessful` | `Boolean` | True after success verification |
| Out | `out_ResultMessage` | `String` | Sanitized outcome detail |

## Validation and business rules

Use **Assign** to trim each `DataRow` value. Use **If** activities and `DateTime.TryParseExact` / `TimeSpan.TryParseExact` with invariant culture. Use **Throw** with `New UiPath.Core.BusinessRuleException("...")` when a rule fails.

- `employee_id`, `employee_name`, `date`, and `status` are required.
- Status is exactly `Present`, `Absent`, or `Leave` after approved case normalization.
- Date uses `yyyy-MM-dd`.
- Time uses `HH:mm`.
- Present requires check-in; check-out is optional.
- Absent and Leave must have empty check-in and check-out.
- When both times exist, check-out cannot precede check-in.

Validation must happen before clicking or typing. This keeps bad business data separate from application failures and prevents partially entered forms.

## Web form interaction

1. Set `out_SubmissionSuccessful = False`.
2. **Click** the stable `Add / Update` link and **Check App State** for the form heading.
3. **Type Into** the employee ID field (`id='employee_id'`), with empty-field behavior enabled.
4. **Type Into** employee name (`id='employee_name'`).
5. Enter date (`id='date'`). Prefer **Type Into** with the browser-compatible formatted value; verify the actual input value. If browser date controls behave differently, use a small tested keyboard sequence rather than coordinates.
6. Use **Select Item** on the status dropdown (`id='status'`) with the validated status.
7. If status is Present, use **Type Into** for `check_in_time` and, when present, `check_out_time`. For Absent/Leave, verify time controls are disabled and do not interact with them.
8. Use **Click** on `Save attendance`.
9. Use **Check App State** for the dashboard success alert containing `Attendance record created successfully.` or `Attendance record updated successfully.`
10. Set `out_SubmissionSuccessful = True` and `out_ResultMessage = "Attendance saved"`.

The employee ID/date pair identifies a record. Reprocessing the same pair is expected to update it, not create a duplicate.

## Success verification

Do not treat a successful click as a successful transaction. Verify the green success alert and the dashboard state. Optionally locate the employee ID and date row on the dashboard as secondary evidence. If an application validation message appears, capture its text; determine whether it indicates missed robot validation (business defect) or an unexpected application condition.

## Exception handling

### Business exceptions

Catch `UiPath.Core.BusinessRuleException` in `Main.xaml`, add a `BUSINESS_EXCEPTION` result, increment `businessExceptionCount`, log a Warning, and continue with the next row. Examples:

- Missing employee ID or name
- Invalid attendance status
- Invalid date/time format
- Present without check-in
- Times supplied for Absent/Leave
- Check-out earlier than check-in

Do not retry unchanged invalid data and do not take a failure screenshot unless it helps demonstrate test evidence.

### System exceptions

Let unexpected `System.Exception` types propagate to the row-level Catch in `Main.xaml`. Add a `SYSTEM_EXCEPTION` result, increment `systemExceptionCount`, capture a screenshot, restore the browser to a known dashboard/form state if possible, and continue only when the session remains usable. Examples:

- Browser or UI element cannot be found
- Selector or application timeout
- Browser crash
- Flask application unavailable
- Success message does not appear

Use a limited **Retry Scope** only for likely transient UI actions. Never retry a form submission blindly: first determine whether it was saved to avoid duplicate or misleading processing.
