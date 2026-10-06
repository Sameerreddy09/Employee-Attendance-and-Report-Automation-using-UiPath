# Test Cases

These cases cover the implemented Flask application and the planned Phase 2 UiPath workflows. UiPath cases remain pending until they are built and run on Windows.

| Test ID | Scenario | Input | Expected Result | Test Type |
|---|---|---|---|---|
| TC-001 | Valid Present record | EMP201, valid date, Present, check-in 09:00, check-out 17:30 | Form saves; success alert appears; result is `SUCCESS` | UiPath functional / end-to-end |
| TC-002 | Valid Absent record | EMP202, valid date, Absent, blank times | Form saves with no time entry; result is `SUCCESS` | UiPath functional |
| TC-003 | Valid Leave record | EMP203, valid date, Leave, blank times | Form saves with no time entry; result is `SUCCESS` | UiPath functional |
| TC-004 | Missing employee ID | Blank ID with otherwise valid data | `BusinessRuleException`; no form submission; `BUSINESS_EXCEPTION`; next row continues | UiPath negative / business rule |
| TC-005 | Invalid attendance status | EMP106 with status Remote | `BusinessRuleException`; no form submission; `BUSINESS_EXCEPTION`; next row continues | UiPath negative / business rule |
| TC-006 | Invalid date | EMP205 with date `05/10/2026` | Date-format business exception; row rejected and processing continues | UiPath negative / business rule |
| TC-007 | Application unavailable | Flask server stopped or controlled unreachable URL | Connection/navigation system exception logged; screenshot when possible; run stops before processing | UiPath negative / system |
| TC-008 | Login failure | Valid username and controlled invalid secure password | Dashboard is not detected; sanitized login system exception; no transactions processed | UiPath security / negative |
| TC-009 | API success | Running Flask app and valid `/api/attendance` URL | HTTP 200; JSON deserializes; returned count equals records-array count; count logged | Integration |
| TC-010 | API failure | Controlled unavailable API URL or timeout | System exception logged with endpoint/status context; no false count reported | Integration / negative |
| TC-011 | XML success | Running Flask app and valid `/api/attendance/xml` URL | HTTP 200; XML parses; root/schema valid; attendance count logged | Integration |
| TC-012 | Malformed XML | Controlled malformed XML string or mock response | XML parsing system exception is caught and logged; no partial success reported | Unit/integration negative |

For TC-007, TC-010, and TC-012, use controlled configuration or mocks rather than damaging the working Flask application. Never use a real password in test evidence.
