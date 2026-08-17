import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "resume-analyzer-development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{BASE_DIR / 'instance' / 'resume_analyzer.db'}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    UPLOAD_FOLDER = BASE_DIR / "uploads" / "resumes"

    REPORT_FOLDER = BASE_DIR / "reports"

    AI_PROVIDER = os.getenv(
        "AI_PROVIDER",
        "openai"
    ).strip().lower()

    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY",
        ""
    ).strip()

    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-5-mini"
    ).strip()

    AI_TEMPERATURE = float(
        os.getenv(
            "AI_TEMPERATURE",
            "0.2"
        )
    )

    AI_MAX_OUTPUT_TOKENS = int(
        os.getenv(
            "AI_MAX_OUTPUT_TOKENS",
            "3000"
        )
    )

    ALLOWED_EXTENSIONS = {
        "pdf",
        "docx",
        "txt"
    }

    @classmethod
    def is_ai_enabled(cls):
        return bool(
            cls.AI_PROVIDER
            and cls.OPENAI_API_KEY
        )