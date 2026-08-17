import secrets

from pathlib import Path

from werkzeug.utils import secure_filename


def generate_secure_filename(
    original_filename
):

    safe_name = secure_filename(
        original_filename
    )

    random_prefix = secrets.token_hex(
        16
    )

    extension = Path(
        safe_name
    ).suffix.lower()

    return (
        f"{random_prefix}"
        f"{extension}"
    )