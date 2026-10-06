# Recommended UiPath Variables and Arguments

Types use .NET names as displayed or resolved by UiPath Studio. Keep variable scope as narrow as practical.

## Main workflow variables

| Name | Type | Scope | Purpose |
|---|---|---|---|
| `repositoryRoot` | `String` | Main Sequence | Absolute base used to resolve configured paths |
| `configPath` | `String` | Main Sequence | Absolute path to `config.json` |
| `configText` | `String` | Load Configuration | Raw configuration JSON |
| `config` | `Newtonsoft.Json.Linq.JObject` | Main Sequence | Parsed non-secret configuration |
| `applicationUrl` | `String` | Main Sequence | Flask login URL |
| `inputFile` | `String` | Main Sequence | Resolved attendance CSV path |
| `outputFile` | `String` | Main Sequence | Resolved results CSV path |
| `apiEndpoint` | `String` | Main Sequence | JSON API URL |
| `xmlEndpoint` | `String` | Main Sequence | XML service URL |
| `username` | `String` | Main Sequence | Configured development username |
| `password` | `System.Security.SecureString` | Login scope | Password returned by secure credential store |
| `attendanceData` | `System.Data.DataTable` | Main Sequence | CSV transactions |
| `currentRow` | `System.Data.DataRow` | For Each Row | Current attendance transaction |
| `resultData` | `System.Data.DataTable` | Main Sequence | One outcome per input row |
| `runId` | `String` | Main Sequence | Correlation identifier, such as a GUID |
| `successCount` | `Int32` | Main Sequence | Successfully verified submissions |
| `failureCount` | `Int32` | Main Sequence | Total business plus system exceptions, if retained for reporting |
| `businessExceptionCount` | `Int32` | Main Sequence | Invalid business transactions |
| `systemExceptionCount` | `Int32` | Main Sequence | Technical transaction failures |
| `processedAt` | `DateTime` | Row scope | Transaction completion timestamp |
| `automationResult` | `String` | Row scope | SUCCESS, BUSINESS_EXCEPTION, or SYSTEM_EXCEPTION |
| `errorType` | `String` | Row scope | Exception class/category; empty on success |
| `errorMessage` | `String` | Row scope | Sanitized result detail |
| `loginSuccessful` | `Boolean` | Browser scope | Dashboard verification outcome |

## Row-processing variables

| Name | Type | Scope | Purpose |
|---|---|---|---|
| `employeeId` | `String` | Process row | Trimmed employee identifier |
| `employeeName` | `String` | Process row | Trimmed employee name |
| `attendanceDateText` | `String` | Process row | Source date before parsing |
| `attendanceDate` | `DateTime` | Process row | Validated date |
| `attendanceStatus` | `String` | Process row | Normalized status |
| `checkInTimeText` | `String` | Process row | Source check-in text |
| `checkOutTimeText` | `String` | Process row | Source check-out text |
| `checkInTime` | `TimeSpan` | Process row | Parsed check-in value |
| `checkOutTime` | `TimeSpan` | Process row | Parsed check-out value |
| `hasCheckIn` | `Boolean` | Process row | Indicates successful/required check-in parse |
| `hasCheckOut` | `Boolean` | Process row | Indicates optional check-out exists and parses |
| `submissionSuccessful` | `Boolean` | Process row | Success-alert verification result |
| `resultMessage` | `String` | Process row | Sanitized workflow outcome |

## Service workflow variables

| Name | Type | Scope | Purpose |
|---|---|---|---|
| `responseText` | `String` | API/XML workflow | HTTP response body |
| `statusCode` | `Int32` or `System.Net.HttpStatusCode` | API/XML workflow | HTTP status, based on installed activity version |
| `responseJson` | `Newtonsoft.Json.Linq.JObject` | API workflow | Parsed JSON response |
| `xmlDocument` | `System.Xml.Linq.XDocument` | XML workflow | Parsed XML response |
| `attendanceNodes` | `IEnumerable(Of System.Xml.Linq.XElement)` | XML workflow | Attendance elements |
| `apiRecordCount` | `Int32` | Main/API workflow | JSON record count |
| `xmlRecordCount` | `Int32` | Main/XML workflow | XML record count |

## Workflow arguments

| Name | Type | Direction | Workflow / Purpose |
|---|---|---|---|
| `in_ApplicationUrl` | `String` | In | Login: target URL |
| `in_Username` | `String` | In | Login: username |
| `in_Password` | `SecureString` | In | Login: protected password |
| `out_LoginSuccessful` | `Boolean` | Out | Login: verified result |
| `in_AttendanceRow` | `DataRow` | In | Process row: source transaction |
| `out_SubmissionSuccessful` | `Boolean` | Out | Process row: verified save |
| `out_ResultMessage` | `String` | Out | Process row: sanitized detail |
| `in_ApiEndpoint` | `String` | In | API: JSON endpoint |
| `out_RecordCount` | `Int32` | Out | API/XML: parsed record count |
| `out_ResponseJson` | `String` | Out | API: raw JSON when explicitly required |
| `in_XmlEndpoint` | `String` | In | XML: XML endpoint |
| `out_AttendanceData` | `DataTable` | Out | XML: optional extracted records |

If `failureCount` is used, calculate it from the two exception counts rather than incrementing all three independently; this avoids counter drift.
