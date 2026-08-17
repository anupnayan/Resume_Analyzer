import re

from collections import OrderedDict


class ResumeAnalyzer:

    SECTION_ALIASES = {
        "summary": {
            "summary",
            "professional summary",
            "profile",
            "professional profile",
            "objective",
            "career objective",
            "about me",
        },

        "skills": {
            "skills",
            "technical skills",
            "core skills",
            "technical expertise",
            "technologies",
            "skills & technologies",
        },

        "education": {
            "education",
            "academic background",
            "academic qualifications",
            "qualifications",
        },

        "experience": {
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history",
        },

        "projects": {
            "projects",
            "academic projects",
            "personal projects",
            "key projects",
        },

        "certifications": {
            "certifications",
            "certificates",
            "licenses & certifications",
        },

        "achievements": {
            "achievements",
            "accomplishments",
            "awards",
            "honors",
        },
    }

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
    ]

    def analyze(self, text):

        if not text:
            return self.empty_profile()

        cleaned_text = self._clean_text(
            text
        )

        sections = self.extract_sections(
            cleaned_text
        )

        profile = OrderedDict()

        profile["name"] = self.extract_name(
            cleaned_text
        )

        profile["email"] = self.extract_email(
            cleaned_text
        )

        profile["phone"] = self.extract_phone(
            cleaned_text
        )

        profile["links"] = self.extract_links(
            cleaned_text
        )

        profile["summary"] = sections.get(
            "summary",
            ""
        )

        profile["skills"] = self.extract_skills(
            cleaned_text,
            sections.get(
                "skills",
                ""
            )
        )

        profile["education"] = self.extract_list_section(
            sections.get(
                "education",
                ""
            )
        )

        profile["experience"] = self.extract_list_section(
            sections.get(
                "experience",
                ""
            )
        )

        profile["projects"] = self.extract_list_section(
            sections.get(
                "projects",
                ""
            )
        )

        profile["certifications"] = self.extract_list_section(
            sections.get(
                "certifications",
                ""
            )
        )

        profile["achievements"] = self.extract_list_section(
            sections.get(
                "achievements",
                ""
            )
        )

        profile["sections"] = sections

        return profile

    def extract_name(self, text):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return ""

        for line in lines[:8]:

            lower = line.lower()

            if (
                "email" in lower
                or "@" in line
                or "phone" in lower
                or "mobile" in lower
                or "linkedin" in lower
                or "github" in lower
                or "http" in lower
            ):
                continue

            cleaned = re.sub(
                r"[^A-Za-z .'-]",
                "",
                line
            ).strip()

            words = cleaned.split()

            if (
                2 <= len(words) <= 5
                and len(cleaned) >= 4
            ):
                return cleaned

        return ""

    def extract_email(self, text):

        match = re.search(
            r"\b[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text
        )

        return (
            match.group(0)
            if match
            else ""
        )

    def extract_phone(self, text):

        patterns = [
            r"(?:\+91[\s-]?)?[6-9]\d{9}",
            r"\+?\d[\d\s().-]{8,}\d",
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                text
            )

            for match in matches:

                cleaned = re.sub(
                    r"[^\d+]",
                    "",
                    match
                )

                digits = re.sub(
                    r"\D",
                    "",
                    cleaned
                )

                if 10 <= len(digits) <= 15:
                    return match.strip()

        return ""

    def extract_links(self, text):

        urls = re.findall(
            r"https?://[^\s<>()]+",
            text,
            flags=re.IGNORECASE
        )

        cleaned = []

        for url in urls:

            url = url.rstrip(
                ".,;)"
            )

            if url not in cleaned:
                cleaned.append(
                    url
                )

        return cleaned

    def extract_sections(self, text):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        sections = OrderedDict()

        current_section = None
        current_lines = []

        for line in lines:

            normalized = self.normalize_heading(
                line
            )

            detected = self.detect_section(
                normalized
            )

            if detected:

                if current_section:

                    sections[current_section] = (
                        "\n".join(
                            current_lines
                        ).strip()
                    )

                current_section = detected
                current_lines = []

            elif current_section:

                current_lines.append(
                    line
                )

        if current_section:

            sections[current_section] = (
                "\n".join(
                    current_lines
                ).strip()
            )

        return dict(sections)

    def detect_section(self, heading):

        normalized = heading.lower().strip()

        for section_name, aliases in self.SECTION_ALIASES.items():

            if normalized in aliases:
                return section_name

        return None

    def normalize_heading(self, line):

        line = line.strip()

        line = re.sub(
            r"^[•●▪◦\-–—]+",
            "",
            line
        ).strip()

        line = re.sub(
            r"[:：]+$",
            "",
            line
        ).strip()

        return re.sub(
            r"\s+",
            " ",
            line
        )

    def extract_skills(
        self,
        full_text,
        skills_section=""
    ):

        search_text = (
            skills_section
            if skills_section
            else full_text
        )

        lower_text = search_text.lower()

        found = []

        for skill in self.COMMON_SKILLS:

            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(skill.lower())
                + r"(?![a-z0-9])"
            )

            if re.search(
                pattern,
                lower_text
            ):

                if skill not in found:
                    found.append(
                        skill
                    )

        return found

    def extract_list_section(
        self,
        section_text
    ):

        if not section_text:
            return []

        lines = []

        for line in section_text.splitlines():

            line = line.strip()

            if not line:
                continue

            line = re.sub(
                r"^[•●▪◦\-–—*]+",
                "",
                line
            ).strip()

            if line:
                lines.append(
                    line
                )

        return lines

    def _clean_text(self, text):

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

    def empty_profile(self):

        return {
            "name": "",
            "email": "",
            "phone": "",
            "links": [],
            "summary": "",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
            "sections": {},
        }


resume_analyzer = ResumeAnalyzer()