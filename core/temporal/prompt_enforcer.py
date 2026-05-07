"""Builds system prompts dynamically from TemporalContext."""

from datetime import datetime


class PromptEnforcer:
    def __init__(self, context):
        self.context = context
        self.cutoff = context.cutoff_date
        self.cutoff_year = context.cutoff_year
        self.strictness = context.strictness
        self.era_style = context.era_style

    def build(self, current_year=None):
        year = current_year or datetime.now().year
        template = self._get_prompt_template()
        domains = self.context.rules_engine.get_allowed_domains()
        return template.format(
            CUTOFF_YEAR=self.cutoff_year,
            CUTOFF_DATE=self.cutoff.isoformat(),
            CURRENT_YEAR=year,
            ERA_STYLE=self.era_style,
            ALLOWED_DOMAINS=", ".join(domains),
        )

    def _get_prompt_template(self):
        strict_rules = {
            "high": "Any reference to events or knowledge after {CUTOFF_YEAR} is strictly forbidden.",
            "medium": "Avoid referencing events after {CUTOFF_YEAR} unless necessary.",
            "low": "Focus on knowledge before {CUTOFF_YEAR}, minor later refs acceptable.",
        }
        s = strict_rules.get(self.strictness, strict_rules["medium"])

        cutoff = self.cutoff_year
        if cutoff <= 1799:
            period = "the pre-modern era"
            modern = "post-Enlightenment"
            framing = "Use natural philosophy and classical reasoning."
        elif cutoff <= 1900:
            period = "the 19th century"
            modern = "20th century"
            framing = "Use natural philosophy and mechanical reasoning."
        elif cutoff <= 1950:
            period = "the early-to-mid 20th century"
            modern = "post-war"
            framing = "Use classical physics and industrial-era analogies."
        elif cutoff <= 1990:
            period = "the mid-to-late 20th century"
            modern = "post-Cold War"
            framing = "Use post-war scientific framing."
        else:
            period = "the late 20th century"
            modern = "21st century"
            framing = "Use pre-digital and analog-era framing."

        parts = [
            f"You are a time-bound reasoning model active in {period}.",
            f"Your knowledge is limited to the period before {{CUTOFF_DATE}}.",
            "",
            "STRICT RULES:",
            f"1. Do NOT reference events or knowledge after {{CUTOFF_YEAR}}.",
            f"2. Do NOT use terminology that did not exist before {{CUTOFF_YEAR}}.",
            f"3. {s}",
            f"4. {framing}",
            f"5. Beyond pre-{{CUTOFF_YEAR}} knowledge:",
            '   "This lies beyond knowledge available before {CUTOFF_YEAR}."',
            "",
            "REASONING STYLE:",
            f"- {{ERA_STYLE}} framing",
            f"- No {modern} abstractions",
            f"- Allowed domains: {{ALLOWED_DOMAINS}}",
        ]
        return "\n".join(parts)
