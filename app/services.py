import csv
from datetime import date, time
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Attendance


VALID_STATUSES = {"Present", "Absent", "Leave"}
REQUIRED_FIELDS = {"employee_id", "employee_name", "date", "status"}


class ValidationError(ValueError):
    pass


def validate_attendance(data):
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    missing = [field for field in REQUIRED_FIELDS if not str(data.get(field, "")).strip()]
    if missing:
        raise ValidationError(f"Missing required fields: {', '.join(sorted(missing))}.")

    employee_id = str(data["employee_id"]).strip()
    employee_name = str(data["employee_name"]).strip()
    status = str(data["status"]).strip().title()

    if len(employee_id) > 30:
        raise ValidationError("employee_id must be 30 characters or fewer.")
    if len(employee_name) > 100:
        raise ValidationError("employee_name must be 100 characters or fewer.")
    if status not in VALID_STATUSES:
        raise ValidationError("status must be Present, Absent, or Leave.")

    try:
        attendance_date = date.fromisoformat(str(data["date"]).strip())
    except ValueError as exc:
        raise ValidationError("date must use YYYY-MM-DD format.") from exc

    check_in = _parse_time(data.get("check_in_time"), "check_in_time")
    check_out = _parse_time(data.get("check_out_time"), "check_out_time")

    if status == "Present" and check_in is None:
        raise ValidationError("check_in_time is required when status is Present.")
    if status != "Present" and (check_in or check_out):
        raise ValidationError("Check-in and check-out times are only allowed for Present records.")
    if check_in and check_out and check_out < check_in:
        raise ValidationError("check_out_time cannot be earlier than check_in_time.")

    return {
        "employee_id": employee_id,
        "employee_name": employee_name,
        "date": attendance_date,
        "status": status,
        "check_in_time": check_in,
        "check_out_time": check_out,
    }


def create_or_update_attendance(data):
    cleaned = validate_attendance(data)
    record = Attendance.query.filter_by(
        employee_id=cleaned["employee_id"], date=cleaned["date"]
    ).first()
    created = record is None
    if created:
        record = Attendance()

    for field, value in cleaned.items():
        setattr(record, field, value)
    if created:
        db.session.add(record)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return record, created


def list_attendance():
    return Attendance.query.order_by(Attendance.date.desc(), Attendance.employee_id).all()


def load_sample_data(csv_path):
    path = Path(csv_path)
    if Attendance.query.first() or not path.exists():
        return 0

    count = 0
    with path.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            cleaned = validate_attendance(row)
            db.session.add(Attendance(**cleaned))
            count += 1
    db.session.commit()
    return count


def _parse_time(value, field_name):
    if value is None or str(value).strip() == "":
        return None
    try:
        return time.fromisoformat(str(value).strip())
    except ValueError as exc:
        raise ValidationError(f"{field_name} must use HH:MM format.") from exc
