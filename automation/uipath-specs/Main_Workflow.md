# Main Workflow Specification

**Planned file:** `Main.xaml`  
**Implementation status:** Design only; to be built and tested in UiPath Studio on Windows.

## Process flow

```text
START
  |
Load Configuration
  |
Read Attendance CSV
  |
Open Browser -> Login
  |
For Each Attendance Record
  |-- Validate Record
  |     |-- invalid -> Record Business Exception -> next row
  |     `-- valid -> Enter in Web UI -> Verify Result
  |                    |-- success -> Record Success
  |                    `-- failure -> Record System Exception
  |
Generate Automation Results
  |
Log Summary
  |
Close Browser
  |
END
```

Use a top-level **Try Catch** inside a **Sequence** and place browser cleanup in a **Finally** block. Row-level exceptions are handled inside the loop so one bad transaction does not stop later rows. Fatal initialization errors stop the run.

## Arguments

`Main.xaml` is the entry point and requires no input arguments. If invoked by another workflow, expose `out_ResultData` (`System.Data.DataTable`) and the three count outputs as `Int32`.

## Step specifications

### 1. Start and initialize

- **Purpose:** Create run state and make the execution traceable.
- **Activities:** **Sequence**, **Assign**, **Build Data Table**, **Log Message**.
- **Inputs:** None.
- **Outputs:** `runId` (`String`), `successCount`, `businessExceptionCount`, `systemExceptionCount` (`Int32`), `resultData` (`DataTable`).
- **Expected result:** Counts are zero; the result table has the seven columns defined in the sample output; a start message includes `runId`.
- **Possible exceptions:** Unexpected DataTable schema or initialization failure. Treat as a fatal system exception.

### 2. Load configuration

- **Purpose:** Read non-secret runtime settings from `automation/config/config.json`.
- **Activities:** **Read Text File**, **Deserialize JSON** (UiPath WebAPI activities), **Assign**, **Path.Combine**, **File Exists**.
- **Inputs:** `configPath` (`String`).
- **Outputs:** `config` (`Newtonsoft.Json.Linq.JObject`) and strings such as `applicationUrl`, `inputFile`, and `outputFile`.
- **Expected result:** All required keys are present, URLs are absolute, and file paths are resolved from the repository root.
- **Possible exceptions:** `FileNotFoundException`, invalid JSON, missing key, invalid URL. These are fatal configuration/system exceptions; log and stop before opening a browser.

### 3. Read attendance CSV

- **Purpose:** Load transactions while preserving empty time fields.
- **Activities:** **Read CSV** with headers enabled; optionally **File Exists** first.
- **Inputs:** `inputFile` (`String`).
- **Outputs:** `attendanceData` (`System.Data.DataTable`).
- **Expected result:** A DataTable contains the six required columns and approximately ten rows.
- **Possible exceptions:** Missing/locked file, access denied, malformed CSV, or missing columns. Missing file/schema is fatal; row values are validated later.

### 4. Open browser

- **Purpose:** Create one reusable browser session for UI automation.
- **Activities:** **Use Application/Browser** targeting Chrome or Edge, with `applicationUrl` as the URL.
- **Inputs:** `applicationUrl` (`String`).
- **Outputs:** Browser/application scope available to child activities; optionally `browser` (`UiPath.Core.Browser`) in classic projects.
- **Expected result:** The login page is visible within the configured timeout.
- **Possible exceptions:** Browser unavailable, extension missing, application unreachable, or timeout. Take a screenshot when possible, log a system exception, and end the run.

### 5. Login

- **Purpose:** Establish the authenticated browser session once.
- **Activities:** **Invoke Workflow File** for `Login.xaml` inside the browser scope.
- **Inputs:** `in_Username` (`String`), `in_Password` (`SecureString`), `in_ApplicationUrl` (`String`).
- **Outputs:** `out_LoginSuccessful` (`Boolean`).
- **Expected result:** Dashboard heading and Add/Update link are visible.
- **Possible exceptions:** Credential retrieval failure, selector timeout, invalid credentials, or navigation failure. Treat as a fatal system exception after any configured retry. See [Login_Workflow.md](Login_Workflow.md).

### 6. For each attendance record

- **Purpose:** Process every source transaction independently.
- **Activities:** **For Each Row in Data Table**, nested **Try Catch**, and **Invoke Workflow File** for `ProcessAttendanceRow.xaml`.
- **Inputs:** `attendanceData` (`DataTable`), `currentRow` (`DataRow`).
- **Outputs:** `automationResult`, `errorType`, `errorMessage` (`String`) and updated counters/result table.
- **Expected result:** Every source row adds exactly one result row.
- **Possible exceptions:** `BusinessRuleException` or a system `Exception`. Never leave a processed row without a result entry.

#### 6a. Validate record

- **Purpose:** Enforce business rules before interacting with the UI.
- **Activities:** **Assign**, **If**, **Is Match** or `DateTime.TryParseExact`, and **Throw**.
- **Inputs:** `currentRow` (`DataRow`).
- **Outputs:** Clean field strings and `isValid` (`Boolean`) or a thrown `UiPath.Core.BusinessRuleException`.
- **Expected result:** Valid rows proceed; invalid rows skip all UI activities.
- **Possible exceptions:** Missing employee ID/name/date/status, invalid status/date/time, missing Present check-in, inappropriate times for Absent/Leave, or check-out before check-in. Handle as business exceptions.

#### 6b. Enter attendance in web application

- **Purpose:** Demonstrate browser-based data entry and update behavior.
- **Activities:** **Click**, **Type Into**, **Select Item**, and **Invoke Workflow File**.
- **Inputs:** Validated employee, date, status, and time values.
- **Outputs:** `out_SubmissionSuccessful` (`Boolean`).
- **Expected result:** The form is submitted once and the browser returns to the dashboard.
- **Possible exceptions:** Selector not found, stale page, timeout, browser crash, or application error. Handle as system exceptions. See [Process_Attendance_Workflow.md](Process_Attendance_Workflow.md).

#### 6c. Verify and record result

- **Purpose:** Confirm the application accepted the transaction and create an auditable result.
- **Activities:** **Check App State** or **Element Exists** for the success alert; **Add Data Row**; **Increment** or **Assign** counters; **Log Message**.
- **Inputs:** Form result and current transaction fields.
- **Outputs:** A result row with `SUCCESS`, `BUSINESS_EXCEPTION`, or `SYSTEM_EXCEPTION`; updated counts.
- **Expected result:** A success alert produces `SUCCESS`; caught exceptions produce their corresponding category and sanitized message.
- **Possible exceptions:** Verification selector timeout or failure to add a result row. Verification failure is a system exception; failure to build results is fatal because the audit output would be incomplete.

### 7. Generate automation results

- **Purpose:** Persist one outcome per input row.
- **Activities:** **Create Folder** (if needed), **Write CSV** with headers.
- **Inputs:** `resultData` (`DataTable`), `outputFile` (`String`).
- **Outputs:** `automation/output/automation_results.csv`.
- **Expected result:** Output count equals input count and columns match the defined sample.
- **Possible exceptions:** Directory unavailable, file locked, access denied, or disk full. Log as a system exception and fail the run because the audit artifact was not produced.

### 8. Optional API and XML checks

- **Purpose:** Demonstrate service integration after UI processing without replacing UI automation.
- **Activities:** Invoke future `API_Workflow.xaml` and `XML_Workflow.xaml`.
- **Inputs:** `apiEndpoint`, `xmlEndpoint` (`String`).
- **Outputs:** `apiRecordCount`, `xmlRecordCount` (`Int32`).
- **Expected result:** Both endpoints respond successfully and return parseable data.
- **Possible exceptions:** Timeout, non-success HTTP code, malformed JSON/XML. Log separately; decide in configuration whether these checks affect overall status.

### 9. Log summary

- **Purpose:** Record a concise completion result.
- **Activities:** **Log Message** at Information level.
- **Inputs:** `runId` and all counts.
- **Outputs:** Log entry containing input, success, business exception, and system exception totals.
- **Expected result:** `successCount + businessExceptionCount + systemExceptionCount = attendanceData.Rows.Count`.
- **Possible exceptions:** Count mismatch should be logged as an Error and fail reconciliation.

### 10. Close browser and end

- **Purpose:** Release resources even after a failure.
- **Activities:** The **Use Application/Browser** scope normally closes its session; otherwise use **Close Tab** or **Close Application** in **Finally**. Finish with **Log Message**.
- **Inputs:** Browser scope/reference and `runId`.
- **Outputs:** Closed browser session and final log entry.
- **Expected result:** No browser instance started by the robot remains open.
- **Possible exceptions:** Cleanup failure. Log a Warning without masking the original exception.

## Recommended package areas

Select package versions compatible with the Windows UiPath Studio project: UI Automation, System, WebAPI, and optionally Testing activities. Record exact package versions in the future UiPath project and avoid unnecessary packages.
