from services.ai_service import get_ai_service


class InterviewService:

    def generate_questions(
        self,
        resume_text: str,
        job_description: str = "",
        count: int = 10
    ) -> dict:

        ai_service = get_ai_service()

        return ai_service.generate_interview_questions(
            resume_text=resume_text,
            job_description=job_description,
            count=count
        )

    def evaluate_answer(
        self,
        question: str,
        answer: str
    ) -> dict:

        ai_service = get_ai_service()

        prompt = f"""
Evaluate this interview answer.

QUESTION:
{question}

ANSWER:
{answer}

Return JSON:

{{
    "communication": 0,
    "technical_knowledge": 0,
    "confidence": 0,
    "relevance": 0,
    "overall": 0,
    "feedback": ""
}}

Scores must be between 0 and 100.
"""

        return ai_service.generate_json(
            prompt=prompt,
            system_prompt=(
                "You are an expert interview evaluator."
            )
        )


interview_service = InterviewService()