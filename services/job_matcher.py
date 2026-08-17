import re


class JobMatcher:

    COMMON_SKILLS = [
        "python",
        "java",
        "javascript",
        "typescript",
        "c",
        "c++",
        "c#",
        "html",
        "css",
        "react",
        "angular",
        "vue",
        "flask",
        "django",
        "fastapi",
        "node.js",
        "express",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "redis",
        "git",
        "github",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "data science",
        "pandas",
        "numpy",
        "scikit-learn",
        "tensorflow",
        "pytorch",
        "rest api",
        "rest",
        "api",
        "linux",
        "power bi",
        "tableau",
        "ci/cd",
        "jenkins",
        "terraform",
        "system design",
    ]

    SOFT_SKILLS = [
        "communication",
        "leadership",
        "teamwork",
        "problem solving",
        "problem-solving",
        "collaboration",
        "time management",
        "adaptability",
        "critical thinking",
        "creativity",
        "analytical thinking",
        "presentation",
        "interpersonal skills",
    ]

    def analyze_job_description(
        self,
        description
    ):
        """
        Extract structured information from a
        job description without using an AI provider.
        """

        if not description:
            return self.empty_profile()

        text = self.clean_text(
            description
        )

        lower_text = text.lower()

        profile = {
            "required_skills": [],
            "preferred_skills": [],
            "experience": "",
            "education": "",
            "responsibilities": [],
            "technologies": [],
            "keywords": [],
            "soft_skills": [],
        }

        profile["required_skills"] = (
            self.extract_skills_from_section(
                text,
                [
                    "required skills",
                    "requirements",
                    "required",
                    "must have",
                    "qualifications",
                ]
            )
        )

        profile["preferred_skills"] = (
            self.extract_skills_from_section(
                text,
                [
                    "preferred skills",
                    "preferred",
                    "nice to have",
                    "good to have",
                    "desired skills",
                ]
            )
        )

        profile["technologies"] = (
            self.extract_known_skills(
                lower_text
            )
        )

        profile["soft_skills"] = (
            self.extract_soft_skills(
                lower_text
            )
        )

        profile["experience"] = (
            self.extract_experience(
                text
            )
        )

        profile["education"] = (
            self.extract_education(
                text
            )
        )

        profile["responsibilities"] = (
            self.extract_responsibilities(
                text
            )
        )

        profile["keywords"] = (
            self.extract_keywords(
                text
            )
        )

        return profile

    def extract_known_skills(
        self,
        text
    ):

        found = []

        for skill in self.COMMON_SKILLS:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(skill.lower())
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                text
            ):

                if skill not in found:
                    found.append(skill)

        return found

    def extract_soft_skills(
        self,
        text
    ):

        found = []

        for skill in self.SOFT_SKILLS:

            if skill.lower() in text:

                if skill not in found:
                    found.append(skill)

        return found

    def extract_skills_from_section(
        self,
        text,
        section_names
    ):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        found = []

        inside_section = False

        for line in lines:

            lower_line = line.lower().strip()

            normalized = re.sub(
                r"[:：]+$",
                "",
                lower_line
            ).strip()

            if any(
                normalized == name
                or normalized.startswith(
                    name + ":"
                )
                for name in section_names
            ):

                inside_section = True

                # Check same-line content.
                parts = line.split(
                    ":",
                    1
                )

                if len(parts) == 2:

                    inline_text = parts[1]

                    found.extend(
                        self.extract_known_skills(
                            inline_text.lower()
                        )
                    )

                continue

            if inside_section:

                # Stop at another heading-like line.
                if self.is_heading(line):

                    inside_section = False

                    continue

                found.extend(
                    self.extract_known_skills(
                        line.lower()
                    )
                )

        return self.unique_items(
            found
        )

    def extract_experience(
        self,
        text
    ):

        patterns = [
            r"\b\d+\+?\s*(?:years?|yrs?)"
            r"\s*(?:of)?\s*experience\b",

            r"\bexperience\s*[:\-]?\s*"
            r"\d+\+?\s*(?:years?|yrs?)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:
                return match.group(0)

        return ""

    def extract_education(
        self,
        text
    ):

        education_keywords = [
            "bachelor",
            "b.tech",
            "btech",
            "b.e.",
            "be ",
            "master",
            "m.tech",
            "mtech",
            "m.e.",
            "mba",
            "phd",
            "degree",
            "computer science",
            "engineering",
        ]

        lines = []

        for line in text.splitlines():

            lower = line.lower()

            if any(
                keyword in lower
                for keyword in education_keywords
            ):

                lines.append(
                    line.strip()
                )

        return "\n".join(
            self.unique_items(
                lines
            )
        )

    def extract_responsibilities(
        self,
        text
    ):

        lines = []

        inside_section = False

        responsibility_headings = [
            "responsibilities",
            "what you'll do",
            "what you will do",
            "role",
            "duties",
            "job responsibilities",
        ]

        for line in text.splitlines():

            clean_line = line.strip()

            if not clean_line:
                continue

            lower = clean_line.lower()

            if any(
                heading in lower
                for heading in responsibility_headings
            ):

                inside_section = True

                continue

            if inside_section:

                if self.is_heading(
                    clean_line
                ):

                    inside_section = False

                    continue

                if (
                    clean_line.startswith("-")
                    or clean_line.startswith("•")
                    or clean_line.startswith("*")
                    or len(clean_line.split()) >= 5
                ):

                    clean_line = re.sub(
                        r"^[•*\-–—]+",
                        "",
                        clean_line
                    ).strip()

                    lines.append(
                        clean_line
                    )

        return self.unique_items(
            lines
        )[:20]

    def extract_keywords(
        self,
        text
    ):

        known_skills = self.extract_known_skills(
            text.lower()
        )

        keywords = []

        for skill in known_skills:

            keywords.append(
                skill
            )

        # Add common job-related terms.
        common_keywords = [
            "backend",
            "frontend",
            "full stack",
            "software development",
            "web development",
            "api development",
            "database",
            "cloud",
            "testing",
            "deployment",
            "agile",
            "scrum",
            "microservices",
            "authentication",
            "authorization",
            "debugging",
            "version control",
        ]

        lower_text = text.lower()

        for keyword in common_keywords:

            if keyword in lower_text:

                if keyword not in keywords:
                    keywords.append(
                        keyword
                    )

        return self.unique_items(
            keywords
        )

    def is_heading(
        self,
        line
    ):

        clean = line.strip()

        if not clean:
            return False

        normalized = re.sub(
            r"[:：]+$",
            "",
            clean.lower()
        ).strip()

        headings = [
            "requirements",
            "required",
            "required skills",
            "preferred",
            "preferred skills",
            "responsibilities",
            "qualifications",
            "education",
            "experience",
            "about the role",
            "what you'll do",
            "what you will do",
            "benefits",
            "nice to have",
            "desired skills",
        ]

        return (
            normalized in headings
        )

    def clean_text(
        self,
        text
    ):

        text = text.replace(
            "\r\n",
            "\n"
        )

        text = text.replace(
            "\r",
            "\n"
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    def unique_items(
        self,
        items
    ):

        result = []

        for item in items:

            item = item.strip()

            if not item:
                continue

            if item.lower() not in [
                existing.lower()
                for existing in result
            ]:

                result.append(
                    item
                )

        return result

    def empty_profile(
        self
    ):

        return {
            "required_skills": [],
            "preferred_skills": [],
            "experience": "",
            "education": "",
            "responsibilities": [],
            "technologies": [],
            "keywords": [],
            "soft_skills": [],
        }


job_matcher = JobMatcher()