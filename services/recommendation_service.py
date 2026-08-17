from services.ai_service import get_ai_service


class RecommendationService:

    def generate(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> dict:

        ai_service = get_ai_service()

        prompt = f"""
Review this resume and provide practical improvement
recommendations.

Resume:
{resume_text}

Job Description:
{job_description or "Not provided."}

Return JSON:

{{
    "recommendations": [
        {{
            "title": "",
            "description": "",
            "priority": "high"
        }}
    ]
}}

Return 5 recommendations maximum.
Do not invent candidate information.
"""

        return ai_service.generate_json(
            prompt=prompt
        )


recommendation_service = RecommendationService()