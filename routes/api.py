from flask import (
    Blueprint,
    jsonify,
    request
)

from services.ai_service import (
    AIServiceError,
    generate_ai_response
)


api_bp = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


@api_bp.route(
    "/ai",
    methods=["POST"]
)
def ai():

    data = request.get_json(
        silent=True
    ) or {}

    prompt = data.get(
        "prompt",
        ""
    ).strip()

    if not prompt:

        return jsonify({
            "success": False,
            "error": "Prompt is required."
        }), 400

    try:

        response = generate_ai_response(
            prompt
        )

        return jsonify({
            "success": True,
            "response": response
        })

    except AIServiceError as exc:

        return jsonify({
            "success": False,
            "error": str(exc),
            "ai_available": False
        }), 503

    except Exception:

        return jsonify({
            "success": False,
            "error": "AI service temporarily unavailable.",
            "ai_available": False
        }), 503