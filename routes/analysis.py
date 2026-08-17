from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash
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

from services import ai_service

try:
    from services.ai_service import AIServiceError
except ImportError:
    class AIServiceError(Exception):
        pass


# ============================================================
# BLUEPRINT
# ============================================================

analysis_bp = Blueprint(
    "analysis",
    __name__,
    url_prefix="/analysis"
)


# ============================================================
# SELECT RESUME + JOB
# ============================================================

@analysis_bp.route("/select", methods=["GET"])
@login_required
def select_resume():

    resumes = (
        Resume.query
        .filter(
            Resume.user_id == current_user.id
        )
        .order_by(
            Resume.created_at.desc()
        )
        .all()
    )

    jobs = (
        JobDescription.query
        .filter(
            JobDescription.user_id == current_user.id
        )
        .order_by(
            JobDescription.created_at.desc()
        )
        .all()
    )

    return render_template(
        "analysis/select.html",
        resumes=resumes,
        jobs=jobs
    )


# ============================================================
# AI CHATBOT
# ============================================================

@analysis_bp.route("/chat", methods=["POST"])
@login_required
def chat():

    data = request.get_json(silent=True) or {}

    message = (
        data.get("message")
        or data.get("prompt")
        or ""
    ).strip()

    if not message:

        return jsonify({
            "success": False,
            "error": "Please enter a message."
        }), 400

    # --------------------------------------------------------
    # GET LATEST USER RESUME
    # --------------------------------------------------------

    latest_resume = (
        Resume.query
        .filter(
            Resume.user_id == current_user.id
        )
        .order_by(
            Resume.created_at.desc()
        )
        .first()
    )

    resume_context = ""

    if latest_resume:

        resume_context = (
            latest_resume.resume_text
            or ""
        ).strip()

    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = """
You are ResumeAI, an AI career and resume assistant.

Your primary purpose is to help users with:

- Resume writing
- Resume improvement
- ATS optimization
- Job descriptions
- Skills
- Career development
- Interview preparation
- Professional summaries
- Cover letters
- Job search preparation

If resume context is available, use it to personalize
your response.

Do not invent information about the user's resume.

If the user asks something unrelated to careers or resumes,
you can still answer briefly, but guide the conversation
back toward career development when appropriate.

Use clear headings and bullet points when useful.

Keep responses practical, professional, and easy to understand.
"""

    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    if resume_context:

        prompt = f"""
User question:

{message}

The user's latest resume text is provided below.

--- RESUME START ---

{resume_context}

--- RESUME END ---

Answer the user's question using the resume context
when relevant.

Do not claim that the resume contains information that
is not actually present.
"""

    else:

        prompt = f"""
User question:

{message}

The user has not uploaded a resume yet.

Answer the question helpfully and, when appropriate,
suggest uploading a resume for personalized analysis.
"""

    # --------------------------------------------------------
    # GENERATE AI RESPONSE
    # --------------------------------------------------------

    try:

        response = ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return jsonify({
            "success": True,
            "response": response
        })

    except AIServiceError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": (
                "AI chatbot failed. "
                f"Reason: {exc}"
            )
        }), 500


# ============================================================
# AI ANALYSIS API
# ============================================================

@analysis_bp.route("/analyze", methods=["POST"])
@login_required
def analyze():

    data = request.get_json(silent=True) or {}

    resume_text = (
        data.get("resume_text")
        or ""
    ).strip()

    job_description = (
        data.get("job_description")
        or ""
    ).strip()

    if not resume_text:

        return jsonify({
            "success": False,
            "error": "Resume text is required."
        }), 400

    # --------------------------------------------------------
    # BUILD ANALYSIS PROMPT
    # --------------------------------------------------------

    prompt = f"""
Analyze the following resume.

RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description}

Provide a structured professional analysis including:

1. ATS score
2. Overall resume score
3. Skills score
4. Experience score
5. Education score
6. Strengths
7. Weaknesses
8. Missing keywords
9. Improvement suggestions
10. Overall recommendations

Do not invent facts about the candidate.

Return the analysis in a clear structured format.
"""

    system_prompt = """
You are ResumeAI, a professional ATS resume analyzer.

Analyze resumes objectively.

Do not invent candidate experience, education,
skills, companies, certifications, or achievements.

If information is missing, explicitly say that it
is missing.

Focus on ATS compatibility, relevance,
clarity, measurable achievements, skills,
formatting, and job alignment.
"""

    # --------------------------------------------------------
    # GENERATE ANALYSIS
    # --------------------------------------------------------

    try:

        response = ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return jsonify({
            "success": True,
            "ai_analysis": response
        })

    except AIServiceError as exc:

        return jsonify({
            "success": False,
            "error": str(exc)
        }), 500

    except Exception as exc:

        return jsonify({
            "success": False,
            "error": (
                "Resume analysis failed. "
                f"Reason: {exc}"
            )
        }), 500


# ============================================================
# RUN ANALYSIS
# ============================================================

@analysis_bp.route(
    "/run/<int:resume_id>/<int:job_id>",
    methods=["GET", "POST"]
)
@login_required
def run_analysis(
    resume_id,
    job_id
):

    # --------------------------------------------------------
    # GET USER RESUME
    # --------------------------------------------------------

    resume = (
        Resume.query
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:

        flash(
            "Resume not found.",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    # --------------------------------------------------------
    # GET USER JOB
    # --------------------------------------------------------

    job = (
        JobDescription.query
        .filter(
            JobDescription.id == job_id,
            JobDescription.user_id == current_user.id
        )
        .first()
    )

    if not job:

        flash(
            "Job description not found.",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    # --------------------------------------------------------
    # GET RESUME TEXT
    # --------------------------------------------------------

    resume_text = (
        resume.resume_text
        or ""
    ).strip()

    if not resume_text:

        flash(
            "This resume does not contain readable text.",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    # --------------------------------------------------------
    # GET JOB DESCRIPTION
    # --------------------------------------------------------

    job_text_parts = []

    if getattr(job, "title", None):
        job_text_parts.append(
            f"Job Title: {job.title}"
        )

    if getattr(job, "company", None):
        job_text_parts.append(
            f"Company: {job.company}"
        )

    if getattr(job, "description", None):
        job_text_parts.append(
            job.description
        )

    if getattr(job, "requirements", None):
        job_text_parts.append(
            f"Requirements:\n{job.requirements}"
        )

    job_text = "\n\n".join(
        job_text_parts
    )

    # --------------------------------------------------------
    # ANALYSIS PROMPT
    # --------------------------------------------------------

    prompt = f"""
Perform a complete ATS and resume analysis.

RESUME:
{resume_text}

TARGET JOB:
{job_text}

Analyze:

- ATS compatibility
- Overall resume quality
- Skills matching
- Experience relevance
- Education relevance
- Missing keywords
- Strengths
- Weaknesses
- Formatting concerns
- Actionable improvements

Do not invent candidate information.

Return a structured analysis.
"""

    system_prompt = """
You are ResumeAI, an expert ATS resume analyzer.

Compare the resume against the target job.

Only use information actually present in the resume
and job description.

Do not invent skills, experience, education,
certifications, employers, or achievements.

Give practical and actionable recommendations.
"""

    # --------------------------------------------------------
    # GENERATE AI ANALYSIS
    # --------------------------------------------------------

    try:

        ai_response = ai_service.generate(
            prompt=prompt,
            system_prompt=system_prompt
        )

    except AIServiceError as exc:

        flash(
            f"AI analysis failed: {exc}",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    except Exception as exc:

        flash(
            f"Analysis failed: {exc}",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    # --------------------------------------------------------
    # CREATE RESUME ANALYSIS
    # --------------------------------------------------------

    analysis = ResumeAnalysis(
        resume_id=resume.id,
        job_id=job.id
    )

    # --------------------------------------------------------
    # STORE AI RESPONSE
    #
    # This safely supports models with different
    # JSON/text analysis columns.
    # --------------------------------------------------------

    if hasattr(
        analysis,
        "ai_analysis"
    ):

        analysis.ai_analysis = ai_response

    elif hasattr(
        analysis,
        "analysis"
    ):

        analysis.analysis = ai_response

    # --------------------------------------------------------
    # SAVE ANALYSIS
    # --------------------------------------------------------

    try:

        from extensions import db

        db.session.add(
            analysis
        )

        db.session.commit()

    except Exception as exc:

        from extensions import db

        db.session.rollback()

        flash(
            f"Could not save analysis: {exc}",
            "error"
        )

        return redirect(
            url_for(
                "analysis.select_resume"
            )
        )

    # --------------------------------------------------------
    # SHOW ATS RESULT
    # --------------------------------------------------------

    return render_template(
        "analysis/ats.html",
        analysis=analysis,
        resume=resume,
        job=job,
        ai_analysis=ai_response
    )