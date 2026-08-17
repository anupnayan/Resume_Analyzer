from flask import (
    Blueprint,
    render_template
)

from flask_login import (
    login_required,
    current_user
)

from models import (
    Resume,
    JobDescription,
    ResumeAnalysis
)


# ============================================================
# MAIN BLUEPRINT
# ============================================================

main_bp = Blueprint(
    "main",
    __name__
)


# ============================================================
# HOME PAGE
# ============================================================

@main_bp.route("/")
def index():

    return render_template(
        "index.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@main_bp.route("/dashboard")
@login_required
def dashboard():

    user_id = current_user.id

    # ========================================================
    # USER RESUMES
    # ========================================================

    resumes = (
        Resume.query
        .filter(
            Resume.user_id == user_id
        )
        .order_by(
            Resume.created_at.desc()
        )
        .all()
    )

    resume_count = len(resumes)

    latest_resume = (
        resumes[0]
        if resumes
        else None
    )

    # ========================================================
    # USER JOB DESCRIPTIONS
    # ========================================================

    jobs = (
        JobDescription.query
        .filter(
            JobDescription.user_id == user_id
        )
        .order_by(
            JobDescription.created_at.desc()
        )
        .all()
    )

    job_count = len(jobs)

    # ========================================================
    # USER RESUME ANALYSES
    #
    # ResumeAnalysis has no user_id column.
    # Therefore we join through Resume.
    # ========================================================

    analyses = (
        ResumeAnalysis.query
        .join(
            Resume,
            ResumeAnalysis.resume_id == Resume.id
        )
        .filter(
            Resume.user_id == user_id
        )
        .order_by(
            ResumeAnalysis.created_at.desc()
        )
        .all()
    )

    analysis_count = len(analyses)

    # ========================================================
    # LATEST ANALYSIS
    # ========================================================

    latest_analysis = (
        analyses[0]
        if analyses
        else None
    )

    # ========================================================
    # ATS SCORE
    # ========================================================

    ats_score = 0

    if latest_analysis:

        ats_score = (
            latest_analysis.ats_score
            or 0
        )

    # ========================================================
    # RESUME SCORE
    # ========================================================

    resume_score = 0

    if latest_analysis:

        resume_score = (
            latest_analysis.overall_score
            or 0
        )

    # ========================================================
    # DETECTED SKILLS
    # ========================================================

    skills = []

    if latest_resume:

        profile = (
            latest_resume.resume_profile
            or {}
        )

        if isinstance(
            profile,
            dict
        ):

            profile_skills = profile.get(
                "skills",
                []
            )

            # ------------------------------------------------
            # FORMAT:
            # "skills": ["Python", "Flask", "SQL"]
            # ------------------------------------------------

            if isinstance(
                profile_skills,
                list
            ):

                skills = profile_skills

            # ------------------------------------------------
            # FORMAT:
            # "skills": {
            #     "technical": [...]
            # }
            # ------------------------------------------------

            elif isinstance(
                profile_skills,
                dict
            ):

                technical = profile_skills.get(
                    "technical",
                    []
                )

                if isinstance(
                    technical,
                    list
                ):

                    skills = technical

    # ========================================================
    # CLEAN SKILLS
    # ========================================================

    unique_skills = []

    seen_skills = set()

    for skill in skills:

        if isinstance(
            skill,
            dict
        ):

            skill_name = (
                skill.get("name")
                or skill.get("skill")
                or ""
            )

        else:

            skill_name = str(
                skill
            )

        skill_name = skill_name.strip()

        skill_key = skill_name.lower()

        if (
            skill_name
            and skill_key not in seen_skills
        ):

            unique_skills.append(
                skill_name
            )

            seen_skills.add(
                skill_key
            )

    skills = unique_skills

    skills_count = len(
        skills
    )

    # ========================================================
    # JOB MATCHES
    #
    # An analysis is considered a job match when it has
    # a linked job description.
    # ========================================================

    job_matches = sum(
        1
        for analysis in analyses
        if analysis.job_id is not None
    )

    # ========================================================
    # RECENT ANALYSES
    # ========================================================

    recent_analyses = analyses[:5]

    # ========================================================
    # DASHBOARD
    # ========================================================

    return render_template(

        "dashboard.html",

        # ----------------------------------------------------
        # CURRENT USER
        # ----------------------------------------------------

        user=current_user,

        # ----------------------------------------------------
        # RESUMES
        # ----------------------------------------------------

        resumes=resumes,

        resume_count=resume_count,

        latest_resume=latest_resume,

        # ----------------------------------------------------
        # JOBS
        # ----------------------------------------------------

        jobs=jobs,

        job_count=job_count,

        # ----------------------------------------------------
        # ANALYSES
        # ----------------------------------------------------

        analyses=analyses,

        analysis_count=analysis_count,

        recent_analyses=recent_analyses,

        latest_analysis=latest_analysis,

        # ----------------------------------------------------
        # SCORES
        # ----------------------------------------------------

        ats_score=ats_score,

        resume_score=resume_score,

        # ----------------------------------------------------
        # SKILLS
        # ----------------------------------------------------

        skills=skills,

        skills_count=skills_count,

        # ----------------------------------------------------
        # JOB MATCHES
        # ----------------------------------------------------

        job_matches=job_matches
    )