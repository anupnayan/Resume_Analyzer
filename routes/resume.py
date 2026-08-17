from pathlib import Path

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from flask_login import (
    current_user,
    login_required
)

from sqlalchemy import select

from extensions import db
from models import Resume

from services.resume_parser import (
    ResumeParserError,
    resume_parser
)

from services.resume_analyzer import (
    resume_analyzer
)

from utils.security import (
    generate_secure_filename
)

from utils.validators import (
    validate_resume_upload
)


resume_bp = Blueprint(
    "resume",
    __name__,
    url_prefix="/resume"
)


@resume_bp.route(
    "/"
)
@login_required
def index():

    resumes = db.session.scalars(
        select(Resume)
        .where(
            Resume.user_id == current_user.id
        )
        .order_by(
            Resume.updated_at.desc()
        )
    ).all()

    return render_template(
        "resume/index.html",
        resumes=resumes
    )


@resume_bp.route(
    "/upload",
    methods=["GET", "POST"]
)
@login_required
def upload():

    if request.method == "POST":

        file = request.files.get(
            "resume"
        )

        valid, error = validate_resume_upload(
            file
        )

        if not valid:

            flash(
                error,
                "danger"
            )

            return render_template(
                "resume/upload.html"
            )

        file_path = None

        try:

            filename = generate_secure_filename(
                file.filename
            )

            upload_folder = Path(
                current_app.config[
                    "UPLOAD_FOLDER"
                ]
            )

            upload_folder.mkdir(
                parents=True,
                exist_ok=True
            )

            file_path = (
                upload_folder
                /
                filename
            )

            file.save(
                file_path
            )

            # ---------------------------------
            # Extract resume text
            # ---------------------------------

            resume_text = resume_parser.extract_text(
                str(file_path)
            )

            # ---------------------------------
            # Analyze resume
            # ---------------------------------

            resume_profile = resume_analyzer.analyze(
                resume_text
            )

            # ---------------------------------
            # Temporarily store profile
            # in Flask session
            # ---------------------------------

            session[
                f"resume_profile_{current_user.id}"
            ] = resume_profile

            # ---------------------------------
            # Save resume and profile
            # in database
            # ---------------------------------

            resume = Resume(
                user_id=current_user.id,
                title=Path(
                    file.filename
                ).stem,
                file_path=str(
                    file_path
                ),
                resume_text=resume_text,
                resume_profile=resume_profile,
                version=1
            )

            db.session.add(
                resume
            )

            db.session.commit()

            flash(
                "Resume uploaded, parsed and analyzed successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "resume.result",
                    resume_id=resume.id
                )
            )

        except ResumeParserError as exc:

            db.session.rollback()

            if file_path:
                Path(
                    file_path
                ).unlink(
                    missing_ok=True
                )

            flash(
                str(exc),
                "danger"
            )

        except Exception as exc:

            db.session.rollback()

            if file_path:
                Path(
                    file_path
                ).unlink(
                    missing_ok=True
                )

            current_app.logger.exception(
                "Resume upload failed: %s",
                exc
            )

            flash(
                "Unable to process the resume.",
                "danger"
            )

    return render_template(
        "resume/upload.html"
    )


@resume_bp.route(
    "/result/<int:resume_id>"
)
@login_required
def result(
    resume_id
):

    resume = get_user_resume(
        resume_id
    )

    if resume is None:

        flash(
            "Resume not found.",
            "danger"
        )

        return redirect(
            url_for(
                "resume.index"
            )
        )

    # ---------------------------------
    # Get profile from database first
    # ---------------------------------

    resume_profile = resume.resume_profile

    # ---------------------------------
    # Fallback to session if necessary
    # ---------------------------------

    if resume_profile is None:

        resume_profile = session.get(
            f"resume_profile_{current_user.id}"
        )

    return render_template(
        "resume/result.html",
        resume=resume,
        resume_profile=resume_profile
    )


@resume_bp.route(
    "/<int:resume_id>"
)
@login_required
def view(
    resume_id
):

    resume = get_user_resume(
        resume_id
    )

    if resume is None:

        flash(
            "Resume not found.",
            "danger"
        )

        return redirect(
            url_for(
                "resume.index"
            )
        )

    return render_template(
        "resume/view.html",
        resume=resume
    )


@resume_bp.route(
    "/<int:resume_id>/delete",
    methods=["POST"]
)
@login_required
def delete(
    resume_id
):

    resume = get_user_resume(
        resume_id
    )

    if resume is None:

        flash(
            "Resume not found.",
            "danger"
        )

        return redirect(
            url_for(
                "resume.index"
            )
        )

    try:

        if resume.file_path:

            Path(
                resume.file_path
            ).unlink(
                missing_ok=True
            )

        # Remove temporary profile
        # from session

        session.pop(
            f"resume_profile_{current_user.id}",
            None
        )

        db.session.delete(
            resume
        )

        db.session.commit()

        flash(
            "Resume deleted successfully.",
            "success"
        )

    except Exception as exc:

        db.session.rollback()

        current_app.logger.exception(
            "Resume deletion failed: %s",
            exc
        )

        flash(
            "Unable to delete resume.",
            "danger"
        )

    return redirect(
        url_for(
            "resume.index"
        )
    )


@resume_bp.route(
    "/<int:resume_id>/version",
    methods=["POST"]
)
@login_required
def create_version(
    resume_id
):

    original = get_user_resume(
        resume_id
    )

    if original is None:

        flash(
            "Resume not found.",
            "danger"
        )

        return redirect(
            url_for(
                "resume.index"
            )
        )

    latest_version = db.session.scalar(
        select(db.func.max(Resume.version))
        .where(
            Resume.user_id == current_user.id,
            Resume.title == original.title
        )
    )

    if latest_version is None:
        latest_version = original.version

    new_version = Resume(
        user_id=current_user.id,
        title=original.title,
        file_path=original.file_path,
        resume_text=original.resume_text,
        resume_profile=original.resume_profile,
        version=latest_version + 1
    )

    db.session.add(
        new_version
    )

    db.session.commit()

    flash(
        f"Resume version {new_version.version} created.",
        "success"
    )

    return redirect(
        url_for(
            "resume.index"
        )
    )


def get_user_resume(
    resume_id
):

    return db.session.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
    )