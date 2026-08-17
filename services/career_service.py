from services.ai_service import get_ai_service


class CareerService:

    def generate_roadmap(
        self,
        current_skills: list[str],
        education: str,
        experience: str,
        target_role: str
    ) -> dict:

        ai_service = get_ai_service()

        return ai_service.generate_career_plan(
            current_skills=current_skills,
            education=education,
            experience=experience,
            target_role=target_role
        )


career_service = CareerService()