from functools import wraps
from xml.etree.ElementTree import Element, SubElement, tostring

from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.exc import SQLAlchemyError

from app.services import ValidationError, create_or_update_attendance, list_attendance


main = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)

    return wrapped


@main.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == current_app.config["BOT_USERNAME"] and password == current_app.config["BOT_PASSWORD"]:
            session["logged_in"] = True
            current_app.logger.info("Automation bot logged in")
            return redirect(url_for("main.dashboard"))
        current_app.logger.warning("Failed login attempt")
        flash("Invalid username or password.", "error")
        return render_template("login.html"), 401
    return render_template("login.html")


@main.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", records=list_attendance())


@main.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    if request.method == "POST":
        try:
            record, created = create_or_update_attendance(request.form.to_dict())
            action = "created" if created else "updated"
            current_app.logger.info("Attendance %s for %s", action, record.employee_id)
            flash(f"Attendance record {action} successfully.", "success")
            return redirect(url_for("main.dashboard"))
        except ValidationError as exc:
            flash(str(exc), "error")
            return render_template("attendance.html", form=request.form), 400
        except SQLAlchemyError:
            current_app.logger.exception("Database error while saving attendance")
            flash("The record could not be saved due to a database error.", "error")
            return render_template("attendance.html", form=request.form), 500
    return render_template("attendance.html", form={})


@main.get("/api/attendance")
def api_get_attendance():
    records = [record.to_dict() for record in list_attendance()]
    return jsonify({"count": len(records), "records": records})


@main.post("/api/attendance")
def api_post_attendance():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415
    try:
        record, created = create_or_update_attendance(request.get_json(silent=True))
        current_app.logger.info("API attendance saved for %s", record.employee_id)
        return jsonify({"message": "Attendance saved.", "record": record.to_dict()}), 201 if created else 200
    except ValidationError as exc:
        current_app.logger.warning("Invalid attendance request: %s", exc)
        return jsonify({"error": str(exc)}), 400
    except SQLAlchemyError:
        current_app.logger.exception("Database error in attendance API")
        return jsonify({"error": "A database error occurred."}), 500


@main.get("/api/attendance/xml")
def api_get_attendance_xml():
    root = Element("attendance_records")
    for record in list_attendance():
        item = SubElement(root, "attendance")
        for key, value in record.to_dict().items():
            SubElement(item, key).text = "" if value is None else str(value)
    return current_app.response_class(
        tostring(root, encoding="utf-8", xml_declaration=True),
        mimetype="application/xml",
    )
