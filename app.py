from pathlib import Path

from flask import Flask

from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(app.config["REPORT_FOLDER"]).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        app.config["REPORT_FOLDER"] / "generated"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        app.config["REPORT_FOLDER"] / "exports"
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    Path(
        app.instance_path
    ).mkdir(
        parents=True,
        exist_ok=True
    )

    db.init_app(app)

    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(
            User,
            int(user_id)
        )

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.resume import resume_bp
    from routes.analysis import analysis_bp
    from routes.jobs import jobs_bp
    from routes.career import career_bp
    from routes.interview import interview_bp
    from routes.reports import reports_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(interview_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )