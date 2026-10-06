import pytest

from app.services import ValidationError, create_or_update_attendance, validate_attendance


def valid_record():
    return {
        "employee_id": "EMP100",
        "employee_name": "Test Employee",
        "date": "2026-10-06",
        "status": "Present",
        "check_in_time": "09:00",
        "check_out_time": "17:30",
    }


def test_validate_attendance_converts_values():
    result = validate_attendance(valid_record())
    assert result["status"] == "Present"
    assert result["date"].isoformat() == "2026-10-06"
    assert result["check_in_time"].strftime("%H:%M") == "09:00"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("status", "Remote", "status must be"),
        ("date", "06/10/2026", "YYYY-MM-DD"),
        ("check_out_time", "08:30", "cannot be earlier"),
    ],
)
def test_validate_attendance_rejects_invalid_data(field, value, message):
    data = valid_record()
    data[field] = value
    with pytest.raises(ValidationError, match=message):
        validate_attendance(data)


def test_create_or_update_uses_employee_and_date(app):
    with app.app_context():
        record, created = create_or_update_attendance(valid_record())
        assert created is True
        updated = valid_record()
        updated["check_out_time"] = "18:00"
        record, created = create_or_update_attendance(updated)
        assert created is False
        assert record.check_out_time.strftime("%H:%M") == "18:00"
