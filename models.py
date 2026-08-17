from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db


# ============================================================
# USER MODEL
# ============================================================

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    resumes = db.relationship(
        "Resume",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    jobs = db.relationship(
        "JobDescription",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


# ============================================================
# RESUME MODEL
# ============================================================

class Resume(db.Model):

    __tablename__ = "resumes"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    resume_text = db.Column(
        db.Text,
        nullable=True
    )

    resume_profile = db.Column(
        db.JSON,
        nullable=True
    )

    version = db.Column(
        db.Integer,
        default=1
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    analyses = db.relationship(
        "ResumeAnalysis",
        back_populates="resume",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ============================================================
# JOB DESCRIPTION MODEL
# ============================================================

class JobDescription(db.Model):

    __tablename__ = "job_descriptions"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    company = db.Column(
        db.String(255),
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    job_profile = db.Column(
        db.JSON,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    analyses = db.relationship(
        "ResumeAnalysis",
        back_populates="job",
        lazy=True,
        cascade="all, delete-orphan"
    )


# ============================================================
# RESUME ANALYSIS MODEL
# ============================================================

class ResumeAnalysis(db.Model):

    __tablename__ = "resume_analyses"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    resume_id = db.Column(
        db.Integer,
        db.ForeignKey("resumes.id"),
        nullable=False
    )

    # --------------------------------------------------------
    # JOB
    # --------------------------------------------------------

    job_id = db.Column(
        db.Integer,
        db.ForeignKey("job_descriptions.id"),
        nullable=True
    )

    # --------------------------------------------------------
    # SCORES
    # --------------------------------------------------------

    overall_score = db.Column(
        db.Float,
        default=0
    )

    ats_score = db.Column(
        db.Float,
        default=0
    )

    content_score = db.Column(
        db.Float,
        default=0
    )

    skills_score = db.Column(
        db.Float,
        default=0
    )

    experience_score = db.Column(
        db.Float,
        default=0
    )

    education_score = db.Column(
        db.Float,
        default=0
    )

    format_score = db.Column(
        db.Float,
        default=0
    )

    impact_score = db.Column(
        db.Float,
        default=0
    )

    # --------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------

    matched_keywords = db.Column(
        db.JSON,
        default=list
    )

    missing_keywords = db.Column(
        db.JSON,
        default=list
    )

    # --------------------------------------------------------
    # ATS FEEDBACK
    # --------------------------------------------------------

    ats_feedback = db.Column(
        db.Text,
        nullable=True
    )

    # --------------------------------------------------------
    # AI FEEDBACK
    # --------------------------------------------------------

    ai_feedback = db.Column(
        db.Text,
        nullable=True
    )

    # --------------------------------------------------------
    # CREATED
    # --------------------------------------------------------

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # --------------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------------

    resume = db.relationship(
        "Resume",
        back_populates="analyses"
    )

    job = db.relationship(
        "JobDescription",
        back_populates="analyses"
    )