from flask import Flask
from app.db import get_db_connection
from app.routes.auth import auth_bp
from app.routes.patient import patient_bp
from app.routes.patientView import general_bp
from app.scheduler import scheduler
from app.routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(general_bp)
    app.register_blueprint(dashboard_bp)
    scheduler.start_scheduler()  # ------- start the scheduler for notification

    return app
