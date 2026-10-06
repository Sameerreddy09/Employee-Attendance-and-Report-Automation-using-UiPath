from datetime import date, time

from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"
    __table_args__ = (
        db.UniqueConstraint("employee_id", "date", name="uq_employee_attendance_date"),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(30), nullable=False, index=True)
    employee_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    status = db.Column(db.String(10), nullable=False)
    check_in_time = db.Column(db.Time, nullable=True)
    check_out_time = db.Column(db.Time, nullable=True)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "date": self.date.isoformat(),
            "status": self.status,
            "check_in_time": _format_time(self.check_in_time),
            "check_out_time": _format_time(self.check_out_time),
        }


def _format_time(value: time | None):
    return value.strftime("%H:%M") if value else None
