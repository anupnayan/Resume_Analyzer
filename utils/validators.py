from pathlib import Path

from flask import current_app


def allowed_file(filename):

    if not filename:
        return False

    extension = Path(
        filename
    ).suffix.lower().lstrip(".")

    return extension in current_app.config[
        "ALLOWED_EXTENSIONS"
    ]


def validate_file_size(file):

    file.seek(
        0,
        2
    )

    size = file.tell()

    file.seek(
        0
    )

    max_size = current_app.config[
        "MAX_CONTENT_LENGTH"
    ]

    return size <= max_size


def validate_resume_upload(file):

    if file is None:
        return False, "No file selected."

    if not file.filename:
        return False, "No filename provided."

    if not allowed_file(
        file.filename
    ):
        return False, (
            "Unsupported file type. "
            "Only PDF, DOCX and TXT files are allowed."
        )

    if not validate_file_size(file):
        return False, (
            "File is too large. "
            "Maximum size is 10 MB."
        )

    return True, None