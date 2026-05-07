"""Temporal context - the single unified system for reasoning
under any temporal cutoff."""

import re
import os
import yaml
from datetime import datetime, date
from typing import Optional

_DEFAULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config", "temporal_defaults.yaml",
)

_PRESETS = {
    "pre_1931": {"cutoff_date": "1931-01-01", "label": "Pre-1931 Historical"},
    "pre_1965": {"cutoff_date": "1965-01-01", "label": "Pre-1965 Mid-Century"},
    "victorian": {"cutoff_date": "1901-01-22", "label": "Victorian Era"},
    "pre_internet": {"cutoff_date": "1995-01-01", "label": "Pre-Internet Era"},
    "cold_war": {"cutoff_date": "1991-12-26", "label": "Cold War Era"},
}

_STRICTNESS_LEVELS = {
    "low": 0.3,
    "medium": 0.6,
    "high": 1.0,
}


class TemporalContext:
    """Single unified temporal constraint system driven by cutoff_date.
    Replaces old TemporalProfile + ProfileRegistry.
    """

    def __init__(self, cutoff_date=None, strictness="medium", preset=None):
        if preset is not None and cutoff_date is None:
            p = _PRESETS.get(preset)
            if p:
                cutoff_date = p["cutoff_date"]
            else:
                raise ValueError(f"Unknown preset: {preset}. Available: {list(_PRESETS.keys())}")
        self.cutoff_date = self._resolve_date(cutoff_date)
        self.cutoff_year = self.cutoff_date.year
        self.strictness = strictness
        self._load_defaults()
        self._rules_engine = None
        self._forbidden_terms = None

    def _resolve_date(self, raw=None):
        if raw and isinstance(raw, str) and raw.lower() in _PRESETS:
            raw = _PRESETS[raw.lower()]["cutoff_date"]
        if raw:
            try:
                return date.fromisoformat(raw)
            except ValueError:
                pass
        env_val = os.environ.get("TEMPORAL_CUTOFF", "")
        if env_val:
            try:
                return date.fromisoformat(env_val)
            except ValueError:
                pass
        return date(1931, 1, 1)

    def _load_defaults(self):
        self._base_terms = []
        self._era_style = "neutral"
        if os.path.exists(_DEFAULTS_PATH):
            try:
                with open(_DEFAULTS_PATH) as f:
                    cfg = yaml.safe_load(f)
                if cfg:
                    self._base_terms = cfg.get("base_forbidden_terms", [])
                    self._era_style = cfg.get("default_style", "neutral")
            except Exception:
                pass

    @property
    def rules_engine(self):
        if self._rules_engine is None:
            from core.temporal.rules_engine import RulesEngine
            self._rules_engine = RulesEngine(self.cutoff_date, self.strictness)
        return self._rules_engine

    @property
    def forbidden_terms(self):
        if self._forbidden_terms is None:
            terms = list(self._base_terms)
            terms.extend(self.rules_engine.generate_forbidden_terms())
            self._forbidden_terms = self._deduplicate(terms)
        return self._forbidden_terms

    def _deduplicate(self, items):
        seen = set()
        result = []
        for item in items:
            lowered = item.lower().strip()
            if lowered and lowered not in seen:
                seen.add(lowered)
                result.append(item)
        return result

    @property
    def compiled_patterns(self):
        return [re.compile(t, re.IGNORECASE) for t in self.forbidden_terms]

    def check(self, text):
        for p in self.compiled_patterns:
            m = p.search(text)
            if m:
                return m.group(0)
        return None

    def check_all(self, text):
        violations = []
        for p in self.compiled_patterns:
            m = p.search(text)
            if m:
                violations.append(m.group(0))
        return violations

    @property
    def system_prompt(self):
        from core.temporal.prompt_enforcer import PromptEnforcer
        enforcer = PromptEnforcer(self)
        return enforcer.build()

    @property
    def era_style(self):
        return self.rules_engine.infer_era_style()

    def to_dict(self):
        return {
            "cutoff_date": self.cutoff_date.isoformat(),
            "cutoff_year": self.cutoff_year,
            "strictness": self.strictness,
            "era_style": self.era_style,
            "forbidden_terms_count": len(self.forbidden_terms),
            "system_prompt_preview": self.system_prompt[:200] + "...",
        }

    @staticmethod
    def presets():
        return _PRESETS

    @staticmethod
    def strictness_options():
        return list(_STRICTNESS_LEVELS.keys())
