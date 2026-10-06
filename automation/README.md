# UiPath Automation — Phase 2 Design Package

This directory prepares the project for UiPath development on Windows. The current macOS environment cannot run UiPath Studio, so **no UiPath workflows or XAML files have been created or tested**. The Markdown specifications are implementation instructions for the future Windows build.

## Contents

```text
config/config.json                     Non-secret runtime settings
input/employee_attendance.csv          Ten demonstration transactions
output/                                Generated run output (Git-ignored)
samples/expected_automation_results.csv Example result formats
uipath-specs/                           Reproducible workflow specifications
```

The input row for **EMP106 / Nikhil Kumar** is intentionally invalid: its status is `Remote`, while the allowed values are `Present`, `Absent`, and `Leave`. The robot should classify this row as a business exception and continue processing.

## Security and configuration

`config.json` contains only non-secret values and a development username. It deliberately does not contain a password. The Windows implementation should retrieve the password as a `SecureString` from a UiPath Orchestrator Credential Asset. Windows Credential Manager is an acceptable local-development alternative. Never commit a password, exported credential, or local credential file.

Paths in `config.json` are repository-relative. In UiPath, resolve them from the project or repository root with `Path.Combine` rather than relying on the current working directory. Keep the Flask server running at the configured URL during UI/API integration testing.

## Suggested Windows implementation order

1. Install UiPath Studio and browser extensions for Chrome or Edge.
2. Create a Windows-compatible UiPath process using the modern design experience.
3. Implement `Login.xaml` from [Login_Workflow.md](uipath-specs/Login_Workflow.md).
4. Implement `ProcessAttendanceRow.xaml` and verify one valid transaction.
5. Assemble `Main.xaml`, CSV input, result collection, and cleanup.
6. Add the API and XML demonstration workflows.
7. Execute the cases in [`../docs/TEST_CASES.md`](../docs/TEST_CASES.md) and save evidence.

The wider design and component responsibilities are documented in [`../docs/TDD.md`](../docs/TDD.md).
