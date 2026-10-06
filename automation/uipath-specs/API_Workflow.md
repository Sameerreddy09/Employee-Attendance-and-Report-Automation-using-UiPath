# REST API Workflow Specification

**Planned file:** `API_Workflow.xaml`  
**Status:** Future design; UI automation remains the primary Phase 2 demonstration.

## GET attendance workflow

| Direction | Name | Type | Purpose |
|---|---|---|---|
| In | `in_ApiEndpoint` | `String` | `/api/attendance` absolute URL |
| Out | `out_RecordCount` | `Int32` | Number of returned records |
| Out | `out_ResponseJson` | `String` | Raw response for controlled downstream use |

1. Use **HTTP Request** from UiPath WebAPI activities with method `GET`, `Accept: application/json`, and a configured timeout.
2. Store response body in `responseText` (`String`) and status in `statusCode` (`Int32`/`HttpStatusCode`, depending on activity version).
3. If the status is not 200, **Throw** a system exception containing only status and endpoint context.
4. Use **Deserialize JSON** to create `responseJson` (`Newtonsoft.Json.Linq.JObject`).
5. Read `count` as `out_RecordCount`. Optionally cross-check it against `responseJson("records").Count` and throw if they differ.
6. Use **Log Message** at Information level: `Attendance API returned {count} records`. Avoid logging the complete payload in normal operation.

Possible exceptions are invalid URL, connection refusal, timeout, non-200 response, malformed JSON, or missing `count`/`records`. Catch to log context and rethrow to the caller.

## POST as an alternative

`POST /api/attendance` accepts an `application/json` object with the six attendance fields. A future API-focused workflow could:

1. Build a `JObject` from a validated row.
2. Serialize it with **Serialize JSON**.
3. Send **HTTP Request** using `POST` and `Content-Type: application/json`.
4. Accept status 201 for creation or 200 for update.
5. Parse the returned `record`, verify employee ID/date, and record the result.
6. Treat HTTP 400 as a business validation exception and connectivity/5xx failures as system exceptions.

This API option is intentionally **not a replacement for browser entry in Phase 2**. The portfolio goal is to demonstrate selectors, browser control, form entry, dropdown handling, and UI verification. Implement the GET workflow as a separate integration demonstration, then optionally compare API and UI approaches.
