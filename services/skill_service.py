class SkillService:

    def calculate_skill_gap(
        self,
        current_skills: list[str],
        target_skills: list[str]
    ) -> dict:

        current = {
            skill.strip().lower()
            for skill in current_skills
        }

        target = {
            skill.strip().lower()
            for skill in target_skills
        }

        matched = sorted(
            current.intersection(target)
        )

        missing = sorted(
            target.difference(current)
        )

        skill_scores = {}

        for skill in target:

            if skill in current:
                skill_scores[skill] = 90

            else:
                skill_scores[skill] = 10

        priorities = []

        for skill in missing:

            priorities.append({
                "skill": skill,
                "priority": self._priority(
                    skill
                )
            })

        priorities.sort(
            key=lambda item: item["priority"]
        )

        return {
            "matched_skills": matched,
            "missing_skills": missing,
            "skill_scores": skill_scores,
            "priorities": priorities
        }

    def _priority(
        self,
        skill: str
    ) -> int:

        high_priority = {
            "python",
            "java",
            "sql",
            "flask",
            "django",
            "docker",
            "aws",
            "machine learning"
        }

        if skill.lower() in high_priority:
            return 1

        return 2


skill_service = SkillService()