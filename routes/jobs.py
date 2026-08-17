from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from extensions import db

from models import JobDescription

from services.job_matcher import job_matcher


# ============================================================
# JOBS BLUEPRINT
# ============================================================

jobs_bp = Blueprint(
    "jobs",
    __name__,
    url_prefix="/jobs"
)


# ============================================================
# JOB LIST
# ============================================================

@jobs_bp.route(
    "/",
    methods=["GET"]
)
@login_required
def index():

    jobs = (
        JobDescription.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            JobDescription.created_at.desc()
        )
        .all()
    )

    return render_template(
        "jobs/jobs.html",
        jobs=jobs
    )


# ============================================================
# CREATE JOB DESCRIPTION
# ============================================================

@jobs_bp.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():

    # ========================================================
    # GET
    # ========================================================

    if request.method == "GET":

        return render_template(
            "jobs/create.html",
            title="",
            company="",
            description=""
        )

    # ========================================================
    # READ FORM DATA
    # ========================================================

    title = (
        request.form.get("title", "")
        or ""
    ).strip()

    company = (
        request.form.get("company", "")
        or ""
    ).strip()

    description = (
        request.form.get("description", "")
        or ""
    ).strip()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not title:

        flash(
            "Please enter a job title.",
            "danger"
        )

        return render_template(
            "jobs/create.html",
            title=title,
            company=company,
            description=description
        )

    if not description:

        flash(
            "Please enter a job description.",
            "danger"
        )

        return render_template(
            "jobs/create.html",
            title=title,
            company=company,
            description=description
        )

    # ========================================================
    # DEFAULT JOB PROFILE
    # ========================================================

    job_profile = {
        "required_skills": [],
        "preferred_skills": [],
        "experience": "",
        "education": "",
        "responsibilities": [],
        "keywords": [],
        "technologies": [],
        "soft_skills": []
    }

    # ========================================================
    # ANALYZE JOB DESCRIPTION
    # ========================================================

    try:

        analyzed_profile = (
            job_matcher.analyze_job_description(
                description
            )
        )

        if isinstance(
            analyzed_profile,
            dict
        ):

            job_profile = analyzed_profile

    except Exception as exc:

        print(
            "[JOB ANALYZER ERROR]",
            exc
        )

        flash(
            "Job description will be saved, "
            "but automatic job analysis was unavailable.",
            "warning"
        )

    # ========================================================
    # CREATE DATABASE OBJECT
    # ========================================================

    try:

        job = JobDescription(
            user_id=current_user.id,
            title=title,
            company=company,
            description=description,
            job_profile=job_profile
        )

        db.session.add(job)

        # Get generated ID before commit
        db.session.flush()

        print(
            "=========================================="
        )
        print(
            "[JOB CREATED]"
        )
        print(
            f"Job ID       : {job.id}"
        )
        print(
            f"User ID      : {job.user_id}"
        )
        print(
            f"Job Title    : {job.title}"
        )
        print(
            f"Company      : {job.company}"
        )
        print(
            "=========================================="
        )

        db.session.commit()

    except Exception as exc:

        db.session.rollback()

        print(
            "[JOB DATABASE ERROR]",
            repr(exc)
        )

        flash(
            f"Could not save job description: {exc}",
            "danger"
        )

        return render_template(
            "jobs/create.html",
            title=title,
            company=company,
            description=description
        )

    # ========================================================
    # VERIFY SAVED JOB
    # ========================================================

    saved_job = (
        JobDescription.query
        .filter_by(
            id=job.id,
            user_id=current_user.id
        )
        .first()
    )

    if not saved_job:

        flash(
            "Job was created but could not be retrieved.",
            "danger"
        )

        return redirect(
            url_for(
                "jobs.create"
            )
        )

    # ========================================================
    # SUCCESS
    # ========================================================

    flash(
        "Job description saved successfully.",
        "success"
    )

    return redirect(
        url_for(
            "jobs.index"
        )
    )


# ============================================================
# VIEW JOB
# ============================================================

@jobs_bp.route(
    "/<int:job_id>",
    methods=["GET"]
)
@login_required
def view_job(job_id):

    job = (
        JobDescription.query
        .filter_by(
            id=job_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    return render_template(
        "jobs/job_match.html",
        job=job
    )


# ============================================================
# DELETE JOB
# ============================================================

@jobs_bp.route(
    "/<int:job_id>/delete",
    methods=["POST"]
)
@login_required
def delete_job(job_id):

    job = (
        JobDescription.query
        .filter_by(
            id=job_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    try:

        db.session.delete(job)

        db.session.commit()

        flash(
            "Job description deleted successfully.",
            "success"
        )

    except Exception as exc:

        db.session.rollback()

        print(
            "[JOB DELETE ERROR]",
            repr(exc)
        )

        flash(
            f"Could not delete job: {exc}",
            "danger"
        )

    return redirect(
        url_for(
            "jobs.index"
        )
    )