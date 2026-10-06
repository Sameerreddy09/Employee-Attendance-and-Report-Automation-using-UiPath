from xml.etree import ElementTree


RECORD = {
    "employee_id": "EMP200",
    "employee_name": "API Employee",
    "date": "2026-10-06",
    "status": "Present",
    "check_in_time": "09:05",
    "check_out_time": "17:45",
}


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_and_dashboard(client):
    response = client.post(
        "/", data={"username": "test_bot", "password": "test_password"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Attendance Dashboard" in response.data


def test_post_and_get_attendance_api(client):
    created = client.post("/api/attendance", json=RECORD)
    assert created.status_code == 201
    assert created.get_json()["record"]["employee_id"] == "EMP200"

    response = client.get("/api/attendance")
    assert response.status_code == 200
    assert response.get_json()["count"] == 1


def test_api_updates_existing_attendance(client):
    client.post("/api/attendance", json=RECORD)
    updated = {**RECORD, "status": "Leave", "check_in_time": None, "check_out_time": None}
    response = client.post("/api/attendance", json=updated)
    assert response.status_code == 200
    assert response.get_json()["record"]["status"] == "Leave"


def test_api_rejects_invalid_input(client):
    response = client.post("/api/attendance", json={"employee_id": "EMP201"})
    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]


def test_api_requires_json(client):
    response = client.post("/api/attendance", data="not-json")
    assert response.status_code == 415


def test_xml_endpoint(client):
    client.post("/api/attendance", json=RECORD)
    response = client.get("/api/attendance/xml")
    assert response.status_code == 200
    assert response.content_type.startswith("application/xml")
    root = ElementTree.fromstring(response.data)
    assert root.tag == "attendance_records"
    assert root.find("attendance/employee_id").text == "EMP200"
