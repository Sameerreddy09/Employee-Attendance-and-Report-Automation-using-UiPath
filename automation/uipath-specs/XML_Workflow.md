# XML Workflow Specification

**Planned file:** `XML_Workflow.xaml`  
**Status:** Design only.

## Arguments

| Direction | Name | Type | Purpose |
|---|---|---|---|
| In | `in_XmlEndpoint` | `String` | Absolute `/api/attendance/xml` URL |
| Out | `out_RecordCount` | `Int32` | Number of `<attendance>` elements |
| Out | `out_AttendanceData` | `System.Data.DataTable` | Optional extracted rows |

## Activity sequence

1. Use **HTTP Request** with method `GET`, `Accept: application/xml`, and a configured timeout.
2. Store the response in `xmlText` (`String`) and verify HTTP status 200 before parsing.
3. Use **Deserialize XML** to create `xmlDocument` (`System.Xml.Linq.XDocument`). If the installed activity produces `XmlDocument`, use its corresponding node APIs consistently.
4. Select child `<attendance>` elements below `<attendance_records>` with an **Assign** expression or **Get XML Nodes**.
5. Set `out_RecordCount` to the node count and log it at Information level.
6. Optionally create `out_AttendanceData` with six columns. Use **For Each** node and **Add Data Row** to extract `employee_id`, `employee_name`, `date`, `status`, `check_in_time`, and `check_out_time` by element name.
7. Validate that the root is `attendance_records`; treat an unexpected schema as a parsing failure.

## Error handling

Wrap request and parsing in **Try Catch**:

- Connection failure, timeout, and non-200 response are system exceptions.
- `XmlException` or `System.Xml.XmlException` indicates malformed XML; log endpoint, run ID, and exception type, then rethrow a sanitized system exception.
- Missing root or required child elements indicate a schema/data-contract failure and should be logged as an Error.
- Never log the full XML by default because production attendance data may be sensitive.

The malformed XML test should use controlled test text or a mock endpoint; do not change the working Flask endpoint merely to force corruption.
