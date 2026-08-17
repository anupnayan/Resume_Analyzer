import re


class ATSService:

    def analyze(
        self,
        resume_profile,
        resume_text,
        job_profile,
        job_description
    ):
        """
        Compare a resume against a job description.

        Returns a deterministic ATS analysis.
        No external AI provider is required.
        """

        resume_profile = (
            resume_profile or {}
        )

        job_profile = (
            job_profile or {}
        )

        resume_text = (
            resume_text or ""
        )

        job_description = (
            job_description or ""
        )

        resume_text_lower = (
            resume_text.lower()
        )

        job_text_lower = (
            job_description.lower()
        )

        # --------------------------------
        # Extract job requirements
        # --------------------------------

        required_skills = self.normalize_list(
            job_profile.get(
                "required_skills",
                []
            )
        )

        preferred_skills = self.normalize_list(
            job_profile.get(
                "preferred_skills",
                []
            )
        )

        job_keywords = self.normalize_list(
            job_profile.get(
                "keywords",
                []
            )
        )

        job_technologies = self.normalize_list(
            job_profile.get(
                "technologies",
                []
            )
        )

        # --------------------------------
        # Build complete keyword set
        # --------------------------------

        target_keywords = self.unique_items(
            required_skills
            + preferred_skills
            + job_keywords
            + job_technologies
        )

        # --------------------------------
        # Find matches
        # --------------------------------

        matched_keywords = []

        missing_keywords = []

        for keyword in target_keywords:

            if self.keyword_exists(
                keyword,
                resume_text_lower
            ):

                matched_keywords.append(
                    keyword
                )

            else:

                missing_keywords.append(
                    keyword
                )

        # --------------------------------
        # Keyword score
        # --------------------------------

        keyword_score = self.calculate_percentage(
            len(matched_keywords),
            len(target_keywords)
        )

        # --------------------------------
        # Skills score
        # --------------------------------

        resume_skills = self.extract_resume_skills(
            resume_profile
        )

        target_skills = self.unique_items(
            required_skills
            + preferred_skills
        )

        matched_skills = []

        for skill in target_skills:

            if self.skill_matches(
                skill,
                resume_skills
            ):

                matched_skills.append(
                    skill
                )

        skills_score = self.calculate_percentage(
            len(matched_skills),
            len(target_skills)
        )

        # --------------------------------
        # Required skills score
        # --------------------------------

        required_matched = []

        for skill in required_skills:

            if self.keyword_exists(
                skill,
                resume_text_lower
            ):

                required_matched.append(
                    skill
                )

        required_score = self.calculate_percentage(
            len(required_matched),
            len(required_skills)
        )

        # --------------------------------
        # Experience score
        # --------------------------------

        experience_score = self.calculate_experience_score(
            resume_profile,
            resume_text,
            job_profile
        )

        # --------------------------------
        # Education score
        # --------------------------------

        education_score = self.calculate_education_score(
            resume_profile,
            resume_text,
            job_profile
        )

        # --------------------------------
        # Formatting score
        # --------------------------------

        format_score = self.calculate_format_score(
            resume_text,
            resume_profile
        )

        # --------------------------------
        # Content score
        # --------------------------------

        content_score = self.calculate_content_score(
            resume_profile,
            resume_text
        )

        # --------------------------------
        # Impact score
        # --------------------------------

        impact_score = self.calculate_impact_score(
            resume_text
        )

        # --------------------------------
        # Overall ATS score
        # --------------------------------

        ats_score = round(
            (
                keyword_score * 0.25
                + skills_score * 0.25
                + experience_score * 0.15
                + education_score * 0.10
                + format_score * 0.15
                + content_score * 0.10
            ),
            2
        )

        overall_score = round(
            (
                ats_score * 0.70
                + impact_score * 0.30
            ),
            2
        )

        feedback = self.generate_feedback(
            ats_score=ats_score,
            keyword_score=keyword_score,
            skills_score=skills_score,
            experience_score=experience_score,
            education_score=education_score,
            format_score=format_score,
            missing_keywords=missing_keywords
        )

        return {
            "overall_score": overall_score,
            "ats_score": ats_score,
            "keyword_score": keyword_score,
            "skills_score": skills_score,
            "required_skills_score": required_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "format_score": format_score,
            "content_score": content_score,
            "impact_score": impact_score,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "matched_skills": matched_skills,
            "feedback": feedback
        }

    # ----------------------------------------
    # Resume skill extraction
    # ----------------------------------------

    def extract_resume_skills(
        self,
        resume_profile
    ):

        skills = []

        skills.extend(
            resume_profile.get(
                "skills",
                []
            )
        )

        skills.extend(
            resume_profile.get(
                "technical_skills",
                []
            )
        )

        skills.extend(
            resume_profile.get(
                "technologies",
                []
            )
        )

        return self.normalize_list(
            skills
        )

    # ----------------------------------------
    # Keyword matching
    # ----------------------------------------

    def keyword_exists(
        self,
        keyword,
        text
    ):

        keyword = keyword.lower().strip()

        if not keyword:
            return False

        # Normalize special characters.
        normalized_keyword = re.sub(
            r"[^a-z0-9+#./-]+",
            " ",
            keyword
        ).strip()

        normalized_text = re.sub(
            r"[^a-z0-9+#./-]+",
            " ",
            text.lower()
        )

        # Direct phrase match.
        if normalized_keyword in normalized_text:
            return True

        # Word-level fallback.
        words = normalized_keyword.split()

        if len(words) == 1:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(words[0])
                + r"(?![a-z0-9])"
            )

            return bool(
                re.search(
                    pattern,
                    normalized_text
                )
            )

        return False

    # ----------------------------------------
    # Skill matching
    # ----------------------------------------

    def skill_matches(
        self,
        target_skill,
        resume_skills
    ):

        target = target_skill.lower().strip()

        for skill in resume_skills:

            existing = skill.lower().strip()

            if target == existing:
                return True

            if target in existing:
                return True

            if existing in target:
                return True

        return False

    # ----------------------------------------
    # Experience
    # ----------------------------------------

    def calculate_experience_score(
        self,
        resume_profile,
        resume_text,
        job_profile
    ):

        required = job_profile.get(
            "experience",
            ""
        )

        if not required:
            return 100

        required_years = self.extract_years(
            required
        )

        if required_years is None:
            return 70

        resume_experience = (
            resume_profile.get(
                "experience",
                []
            )
        )

        resume_experience_text = str(
            resume_experience
        )

        resume_years = self.extract_years(
            resume_experience_text
        )

        if resume_years is None:

            resume_years = self.extract_years(
                resume_text
            )

        if resume_years is None:
            return 50

        if resume_years >= required_years:
            return 100

        if resume_years >= required_years - 1:
            return 80

        if resume_years > 0:
            return 60

        return 30

    def extract_years(
        self,
        text
    ):

        if not text:
            return None

        patterns = [
            r"(\d+)\+?\s*(?:years?|yrs?)",
            r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)"
        ]

        match = re.search(
            patterns[0],
            str(text),
            re.IGNORECASE
        )

        if match:
            return int(
                match.group(1)
            )

        match = re.search(
            patterns[1],
            str(text),
            re.IGNORECASE
        )

        if match:
            return int(
                match.group(2)
            )

        return None

    # ----------------------------------------
    # Education
    # ----------------------------------------

    def calculate_education_score(
        self,
        resume_profile,
        resume_text,
        job_profile
    ):

        required = job_profile.get(
            "education",
            ""
        )

        if not required:
            return 100

        education = str(
            resume_profile.get(
                "education",
                ""
            )
        )

        if not education:
            education = resume_text

        required_words = [
            "bachelor",
            "b.tech",
            "btech",
            "b.e",
            "be ",
            "master",
            "m.tech",
            "mtech",
            "m.e",
            "mba",
            "phd",
            "computer science",
            "engineering"
        ]

        required_lower = required.lower()
        education_lower = education.lower()

        matches = 0

        for word in required_words:

            if word in required_lower:

                if word in education_lower:

                    matches += 1

        total = sum(
            1
            for word in required_words
            if word in required_lower
        )

        if total == 0:
            return 70

        return self.calculate_percentage(
            matches,
            total
        )

    # ----------------------------------------
    # Formatting
    # ----------------------------------------

    def calculate_format_score(
        self,
        resume_text,
        resume_profile
    ):

        score = 100

        if len(resume_text.strip()) < 300:
            score -= 25

        if len(resume_text.strip()) > 15000:
            score -= 10

        sections = [
            "education",
            "experience",
            "skills",
            "projects"
        ]

        lower_text = resume_text.lower()

        section_count = 0

        for section in sections:

            if section in lower_text:
                section_count += 1

        if section_count < 2:
            score -= 20

        if not resume_profile:
            score -= 10

        return max(
            0,
            min(
                100,
                score
            )
        )

    # ----------------------------------------
    # Content
    # ----------------------------------------

    def calculate_content_score(
        self,
        resume_profile,
        resume_text
    ):

        score = 0

        important_sections = [
            "name",
            "email",
            "phone",
            "education",
            "experience",
            "skills",
            "projects"
        ]

        for section in important_sections:

            value = resume_profile.get(
                section
            )

            if value:
                score += 14

        if len(resume_text.strip()) > 500:
            score += 5

        return min(
            100,
            score
        )

    # ----------------------------------------
    # Impact
    # ----------------------------------------

    def calculate_impact_score(
        self,
        resume_text
    ):

        text = resume_text.lower()

        action_verbs = [
            "developed",
            "implemented",
            "designed",
            "created",
            "built",
            "optimized",
            "improved",
            "automated",
            "engineered",
            "deployed",
            "integrated",
            "managed",
            "led",
            "delivered",
            "reduced",
            "increased"
        ]

        metrics = re.findall(
            r"\b\d+(?:\.\d+)?%?\b",
            text
        )

        action_count = 0

        for verb in action_verbs:

            if verb in text:
                action_count += 1

        score = 40

        score += min(
            35,
            action_count * 3
        )

        score += min(
            25,
            len(metrics) * 5
        )

        return min(
            100,
            score
        )

    # ----------------------------------------
    # Feedback
    # ----------------------------------------

    def generate_feedback(
        self,
        ats_score,
        keyword_score,
        skills_score,
        experience_score,
        education_score,
        format_score,
        missing_keywords
    ):

        feedback = []

        if ats_score >= 85:

            feedback.append(
                "Strong ATS compatibility."
            )

        elif ats_score >= 70:

            feedback.append(
                "Good ATS compatibility with room for improvement."
            )

        else:

            feedback.append(
                "The resume needs significant ATS optimization."
            )

        if keyword_score < 70:

            feedback.append(
                "Add more job-specific keywords naturally."
            )

        if skills_score < 70:

            feedback.append(
                "Strengthen the skills section with relevant technologies."
            )

        if experience_score < 70:

            feedback.append(
                "Make professional experience more closely match the target role."
            )

        if education_score < 70:

            feedback.append(
                "Review education requirements for the target position."
            )

        if format_score < 70:

            feedback.append(
                "Improve resume structure and section organization."
            )

        if missing_keywords:

            feedback.append(
                "Consider adding: "
                + ", ".join(
                    missing_keywords[:10]
                )
            )

        return feedback

    # ----------------------------------------
    # Utilities
    # ----------------------------------------

    def calculate_percentage(
        self,
        matched,
        total
    ):

        if total <= 0:
            return 100

        return round(
            (matched / total) * 100,
            2
        )

    def normalize_list(
        self,
        values
    ):

        if not values:
            return []

        if isinstance(
            values,
            str
        ):

            values = [
                values
            ]

        result = []

        for value in values:

            if value is None:
                continue

            value = str(
                value
            ).strip().lower()

            if value:
                result.append(
                    value
                )

        return self.unique_items(
            result
        )

    def unique_items(
        self,
        items
    ):

        result = []

        for item in items:

            item = str(
                item
            ).strip()

            if not item:
                continue

            if item.lower() not in [
                x.lower()
                for x in result
            ]:

                result.append(
                    item
                )

        return result


ats_service = ATSService()