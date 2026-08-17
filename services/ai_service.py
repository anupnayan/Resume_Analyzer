import json
import logging
from typing import Any, Optional

from openai import OpenAI
from openai import AuthenticationError
from openai import APIConnectionError
from openai import APIError
from openai import RateLimitError

from config import Config


logger = logging.getLogger(__name__)


# ============================================================
# EXCEPTIONS
# ============================================================

class AIServiceError(Exception):
    """Base exception for AI service failures."""


class AIAuthenticationError(AIServiceError):
    """Raised when the AI credential is invalid."""


class AIUnavailableError(AIServiceError):
    """Raised when the AI provider cannot be reached."""


# ============================================================
# OPENAI PROVIDER
# ============================================================

class OpenAIProvider:
    """
    OpenAI-specific implementation.

    Only this provider communicates directly with OpenAI.
    """

    def __init__(self):

        if not Config.OPENAI_API_KEY:
            raise AIAuthenticationError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY
        )

        self.model = Config.OPENAI_MODEL

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        instructions = system_prompt or (
            "You are ResumeAI, an expert resume analysis "
            "and career assistant. Give accurate, practical "
            "and professional answers."
        )

        try:

            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=prompt,
                max_output_tokens=(
                    max_output_tokens
                    or Config.AI_MAX_OUTPUT_TOKENS
                )
            )

            text = getattr(
                response,
                "output_text",
                None
            )

            if not text:
                return ""

            return text.strip()

        except AuthenticationError as exc:

            logger.error(
                "OpenAI authentication failed."
            )

            raise AIAuthenticationError(
                "The configured AI credential was rejected."
            ) from exc

        except RateLimitError as exc:

            logger.error(
                "OpenAI rate limit reached."
            )

            raise AIServiceError(
                "AI rate limit reached. Please try again later."
            ) from exc

        except APIConnectionError as exc:

            logger.error(
                "Unable to connect to OpenAI."
            )

            raise AIUnavailableError(
                "Unable to connect to the AI provider."
            ) from exc

        except APIError as exc:

            logger.error(
                "OpenAI API error: %s",
                exc
            )

            raise AIServiceError(
                "The AI provider returned an error."
            ) from exc

        except Exception as exc:

            logger.exception(
                "Unexpected AI error."
            )

            raise AIServiceError(
                "Unexpected AI service error."
            ) from exc


# ============================================================
# GEMINI PROVIDER
# ============================================================

class GeminiProvider:
    """
    Placeholder for future Gemini integration.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:

        raise AIUnavailableError(
            "Gemini provider is not configured yet."
        )


# ============================================================
# LOCAL AI PROVIDER
# ============================================================

class LocalAIProvider:
    """
    Placeholder for future local model integration.
    """

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:

        raise AIUnavailableError(
            "Local AI provider is not configured yet."
        )


# ============================================================
# AI SERVICE
# ============================================================

class AIService:
    """
    Provider-independent AI service.

    Application code should communicate with this class,
    not directly with OpenAI/Gemini/local models.
    """

    def __init__(self):

        provider_name = Config.AI_PROVIDER

        if provider_name == "openai":

            self.provider = OpenAIProvider()

        elif provider_name == "gemini":

            self.provider = GeminiProvider()

        elif provider_name == "local":

            self.provider = LocalAIProvider()

        else:

            raise AIServiceError(
                f"Unsupported AI provider: {provider_name}"
            )

    # ========================================================
    # GENERATE
    # ========================================================

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_output_tokens: Optional[int] = None
    ) -> str:

        return self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_output_tokens=max_output_tokens
        )

    # ========================================================
    # GENERATE JSON
    # ========================================================

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> dict[str, Any]:

        response = self.generate(
            prompt=prompt,
            system_prompt=(
                system_prompt
                or
                "Return only valid JSON. "
                "Do not include markdown fences."
            )
        )

        try:

            return json.loads(response)

        except json.JSONDecodeError as exc:

            logger.error(
                "AI returned invalid JSON: %s",
                response
            )

            raise AIServiceError(
                "AI returned an invalid structured response."
            ) from exc

    # ========================================================
    # ANALYZE RESUME
    # ========================================================

    def analyze_resume(
        self,
        resume_text: str,
        job_description: str = ""
    ) -> dict[str, Any]:

        prompt = f"""
Analyze the following resume professionally.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description or "No job description provided."}

Return JSON with exactly these top-level fields:

{{
    "overall_score": 0,
    "ats_score": 0,
    "content_score": 0,
    "skills_score": 0,
    "experience_score": 0,
    "education_score": 0,
    "format_score": 0,
    "impact_score": 0,
    "strengths": [],
    "weaknesses": [],
    "recommendations": [],
    "missing_keywords": [],
    "candidate_summary": ""
}}

Scores must be integers from 0 to 100.

Do not invent information that is not present
in the resume.
"""

        return self.generate_json(
            prompt=prompt,
            system_prompt=(
                "You are an expert ATS and resume evaluator. "
                "Analyze resumes objectively and return valid JSON only."
            )
        )

    # ========================================================
    # IMPROVE RESUME
    # ========================================================

    def improve_resume(
        self,
        section: str,
        content: str,
        context: Optional[str] = None
    ) -> str:

        prompt = f"""
Improve the following resume section.

SECTION:
{section}

CONTENT:
{content}

CONTEXT:
{context or "No additional context provided."}

Requirements:

1. Preserve factual information.
2. Do not invent employment, education, skills,
   certifications or achievements.
3. Improve professional language.
4. Use strong action verbs.
5. Make the content ATS friendly.
6. Keep it concise.
7. Improve clarity and impact.
8. Do not add unsupported claims.

Return only the improved section.
"""

        return self.generate(
            prompt=prompt,
            system_prompt=(
                "You are an expert professional resume writer "
                "and ATS optimization specialist."
            )
        )

    # ========================================================
    # GENERATE SUMMARY
    # ========================================================

    def generate_summary(
        self,
        resume_text: str,
        target_role: Optional[str] = None
    ) -> str:

        prompt = f"""
Write a strong professional resume summary.

RESUME:
{resume_text}

TARGET ROLE:
{target_role or "Not specified"}

Requirements:

- Base the summary only on information in the resume.
- Do not invent facts.
- Make it ATS friendly.
- Highlight relevant skills and experience.
- Keep it between 3 and 5 sentences.
- Use professional language.
"""

        return self.generate(
            prompt=prompt,
            system_prompt=(
                "You are an expert resume writer."
            )
        )

    # ========================================================
    # GENERATE BULLETS
    # ========================================================

    def generate_bullets(
        self,
        job_or_project: str,
        description: str,
        style: str = "professional"
    ) -> list[str]:

        prompt = f"""
Generate 4 strong resume bullet points.

JOB OR PROJECT:
{job_or_project}

DESCRIPTION:
{description}

STYLE:
{style}

Requirements:

- Begin with strong action verbs.
- Be concise.
- Be ATS friendly.
- Improve professional impact.
- Do not invent technologies.
- Do not invent achievements.
- Do not invent metrics.
- Return JSON only.

Format:

{{
    "bullets": [
        "...",
        "...",
        "...",
        "..."
    ]
}}
"""

        result = self.generate_json(
            prompt=prompt
        )

        bullets = result.get(
            "bullets",
            []
        )

        if not isinstance(bullets, list):
            return []

        return [
            str(item).strip()
            for item in bullets
            if str(item).strip()
        ]

    # ========================================================
    # GENERATE COVER LETTER
    # ========================================================

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        company: str,
        style: str = "professional"
    ) -> str:

        prompt = f"""
Create a professional cover letter.

COMPANY:
{company}

STYLE:
{style}

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Requirements:

- Match the candidate's real experience
  to the job requirements.
- Do not invent facts.
- Avoid generic filler.
- Keep it professional.
- Highlight relevant skills.
- Make it concise.
"""

        return self.generate(
            prompt=prompt,
            system_prompt=(
                "You are an expert career writer."
            )
        )

    # ========================================================
    # GENERATE INTERVIEW QUESTIONS
    # ========================================================

    def generate_interview_questions(
        self,
        resume_text: str,
        target_role: Optional[str] = None,
        count: int = 10
    ) -> dict[str, Any]:

        prompt = f"""
Generate {count} interview questions based on
the candidate's resume.

RESUME:
{resume_text}

TARGET ROLE:
{target_role or "Not provided"}

Return JSON:

{{
    "technical": [],
    "hr": [],
    "resume_based": []
}}

Requirements:

- Questions should be relevant to the candidate.
- Include technical questions where appropriate.
- Include HR questions.
- Include resume-specific questions.
- Avoid generic questions where possible.
"""

        return self.generate_json(
            prompt=prompt,
            system_prompt=(
                "You are an expert technical recruiter "
                "and interview coach."
            )
        )

    # ========================================================
    # GENERATE CAREER PLAN
    # ========================================================

    def generate_career_plan(
        self,
        resume_text: str,
        target_role: str
    ) -> dict[str, Any]:

        prompt = f"""
Create a personalized career roadmap.

RESUME:
{resume_text}

TARGET ROLE:
{target_role}

Return JSON:

{{
    "current_level": "",
    "career_path": [],
    "required_skills": [],
    "responsibilities": [],
    "recommended_projects": [],
    "roadmap": []
}}

Requirements:

- Analyze the candidate based only on the resume.
- Do not invent candidate experience.
- Identify missing skills.
- Recommend practical projects.
- Provide a realistic learning roadmap.
- Tailor everything to the target role.
"""

        return self.generate_json(
            prompt=prompt,
            system_prompt=(
                "You are an expert career advisor "
                "specializing in technology careers."
            )
        )


# ============================================================
# SINGLETON SERVICE
# ============================================================

_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:

    global _ai_service

    if _ai_service is None:

        _ai_service = AIService()

    return _ai_service


# ============================================================
# PUBLIC FUNCTION: generate()
# ============================================================

def generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_output_tokens: Optional[int] = None
) -> str:

    return get_ai_service().generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_output_tokens=max_output_tokens
    )


# ============================================================
# PUBLIC FUNCTION: analyze_resume()
# ============================================================

def analyze_resume(
    resume_text: str,
    job_description: str = ""
) -> dict[str, Any]:

    return get_ai_service().analyze_resume(
        resume_text=resume_text,
        job_description=job_description
    )


# ============================================================
# PUBLIC FUNCTION: improve_resume()
# ============================================================

def improve_resume(
    section: str,
    content: str,
    context: Optional[str] = None
) -> str:

    return get_ai_service().improve_resume(
        section=section,
        content=content,
        context=context
    )


# ============================================================
# PUBLIC FUNCTION: generate_summary()
# ============================================================

def generate_summary(
    resume_text: str,
    target_role: Optional[str] = None
) -> str:

    return get_ai_service().generate_summary(
        resume_text=resume_text,
        target_role=target_role
    )


# ============================================================
# PUBLIC FUNCTION: generate_bullets()
# ============================================================

def generate_bullets(
    job_or_project: str,
    description: str,
    style: str = "professional"
) -> list[str]:

    return get_ai_service().generate_bullets(
        job_or_project=job_or_project,
        description=description,
        style=style
    )


# ============================================================
# PUBLIC FUNCTION: generate_cover_letter()
# ============================================================

def generate_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    style: str = "professional"
) -> str:

    return get_ai_service().generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
        company=company,
        style=style
    )


# ============================================================
# PUBLIC FUNCTION: generate_interview_questions()
# ============================================================

def generate_interview_questions(
    resume_text: str,
    target_role: Optional[str] = None,
    count: int = 10
) -> dict[str, Any]:

    return get_ai_service().generate_interview_questions(
        resume_text=resume_text,
        target_role=target_role,
        count=count
    )


# ============================================================
# PUBLIC FUNCTION: generate_career_plan()
# ============================================================

def generate_career_plan(
    resume_text: str,
    target_role: str
) -> dict[str, Any]:

    return get_ai_service().generate_career_plan(
        resume_text=resume_text,
        target_role=target_role
    )


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def generate_ai_response(
    prompt: str,
    system_prompt: Optional[str] = None
) -> str:

    return generate(
        prompt=prompt,
        system_prompt=system_prompt
    )


# ============================================================
# PUBLIC SERVICE INSTANCE
# ============================================================

ai_service = get_ai_service()