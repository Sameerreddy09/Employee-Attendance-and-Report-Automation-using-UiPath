import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'attendance.db'}"
    ).replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOT_USERNAME = os.getenv("BOT_USERNAME", "attendance_bot")
    BOT_PASSWORD = os.getenv("BOT_PASSWORD", "bot_password")
    SAMPLE_DATA_PATH = BASE_DIR / "data" / "employee_attendance.csv"
    LOG_PATH = BASE_DIR / "logs" / "app.log"
