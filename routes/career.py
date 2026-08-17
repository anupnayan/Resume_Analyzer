from flask import Blueprint


career_bp = Blueprint(
    "career",
    __name__,
    url_prefix="/career"
)