import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(config_object="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)

    from app.routes import main

    app.register_blueprint(main)
    configure_logging(app)

    with app.app_context():
        db.create_all()
        if app.config.get("LOAD_SAMPLE_DATA", True):
            from app.services import load_sample_data

            load_sample_data(app.config["SAMPLE_DATA_PATH"])

    return app


def configure_logging(app):
    if app.testing:
        return

    log_path = Path(app.config["LOG_PATH"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_path, maxBytes=500_000, backupCount=3)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
