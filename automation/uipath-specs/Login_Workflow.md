# Login Workflow Specification

**Planned file:** `Login.xaml`  
**Status:** Design only; implementation requires UiPath Studio on Windows.

## Purpose

Sign the development automation user into the Flask application through Chrome or Edge, confirm the dashboard is loaded, and fail clearly when authentication is unsuccessful.

## Arguments

| Direction | Name | Type | Purpose |
|---|---|---|---|
| In | `in_ApplicationUrl` | `String` | Login page URL |
| In | `in_Username` | `String` | Non-secret development username |
| In | `in_Password` | `System.Security.SecureString` | Password retrieved securely |
| Out | `out_LoginSuccessful` | `Boolean` | True only after dashboard verification |

## Prerequisites

- Install the UiPath extension for the selected Chrome or Edge browser.
- Start the Flask application at the configured URL.
- Store the password as a UiPath Orchestrator **Credential Asset**. For local development, use Windows Credential Manager through an approved credential activity. Do not store a password in JSON, XAML, source control, arguments visible in logs, or screenshots.

## Activity sequence

1. Set `out_LoginSuccessful = False` with **Assign**.
2. Retrieve the credential with **Get Credential** / **Get Credential By Name**. Use the configured asset name once one is added to the environment; keep the returned password as `SecureString`.
3. Use **Use Application/Browser** and navigate to `in_ApplicationUrl`. Choose Chrome or Edge and configure an appropriate timeout.
4. Use **Check App State** for the page heading `Employee Attendance` and username field. If the target does not appear, throw an application-unavailable exception.
5. Use **Type Into** for the username. Empty the field first and type `in_Username`.
6. Use **Type Secure Text** for the password so the plain value is not exposed.
7. Use **Click** on the `Sign in` button.
8. Use **Check App State** for stable dashboard evidence, such as the `Attendance Dashboard` heading and `Add / Update` link.
9. In the target-appeared branch, set `out_LoginSuccessful = True` and log an Information message without credentials.
10. In the target-not-appeared branch, check for the `Invalid username or password.` alert, then **Throw** a new `System.Exception` with a sanitized login failure message.

Wrap the interaction in **Try Catch**. Add context and rethrow so `Main.xaml` can stop safely; login failure is fatal because no transactions can be processed.

## Selectors

Stable selectors make the automation resilient to page layout and styling changes. Use UiPath UI Explorer to prefer semantic attributes such as:

- `id='username'` for the username input
- `id='password'` for the password input
- element type plus visible text `Sign in` for the button
- heading text `Attendance Dashboard` for success verification

Avoid volatile attributes, generated indexes, screen coordinates, and selectors tied to CSS colors or exact element position. Validate selectors at more than one window size. Use **Anchor Base** or modern target/anchor pairs only when a unique stable attribute is unavailable.

## Expected result

The existing browser session displays `/dashboard`, `out_LoginSuccessful` is `True`, and the robot proceeds to attendance processing.

## Possible exceptions

- Credential asset unavailable or access denied
- Browser executable/extension unavailable
- Flask application unavailable
- Login fields or button not found
- Invalid username/password
- Dashboard verification timeout

For a selector or navigation system failure, capture a screenshot if the page does not contain sensitive data, log the run ID and exception type, and rethrow. Do not include the password in any log or result.
