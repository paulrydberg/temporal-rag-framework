import os
import re
import yaml
from datetime import datetime
from typing import Optional

PROFILES_DIR = os.environ.get(
    "TEMPORAL_PROFILES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "temporal_profiles"),
)
DEFAULT_CONFIG = os.path.join(os.path.dirname(PROFILES_DIR), "default.yaml")


class TemporalProfile:
    def __init__(self, data: dict):
        self.name = data.get("name", "default")
        self.label = data.get("label", self.name)
        self.description = data.get("description", "")
        self.cutoff_year = data.get("cutoff_year", 1931)
        self.cutoff_date = data.get("cutoff_date", f"{self.cutoff_year}-01-01")
        self.allowed_domains = data.get("allowed_domains", [])
        self.forbidden_terms = data.get("forbidden_terms", [])
        self.forbidden_concepts = data.get("forbidden_concepts", [])
        self.historical_style = data.get("historical_style", "neutral")
        self.rag_sources = data.get("rag_sources", [])
        self.system_prompt_template = data.get("system_prompt", "")
        self.response_rules = data.get("response_rules", {})
        self._raw = data

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

    def format_system_prompt(self, current_year=None):
        if not self.system_prompt_template:
            return ""
        year = current_year or datetime.now().year
        return self.system_prompt_template.format(
            CUTOFF_YEAR=self.cutoff_year,
            CUTOFF_DATE=self.cutoff_date,
            CURRENT_YEAR=year,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "cutoff_year": self.cutoff_year,
            "cutoff_date": self.cutoff_date,
            "allowed_domains": self.allowed_domains,
            "forbidden_terms_count": len(self.forbidden_terms),
            "forbidden_concepts": self.forbidden_concepts,
            "historical_style": self.historical_style,
            "rag_sources": self.rag_sources,
        }


class ProfileRegistry:
    def __init__(self, profiles_dir=None):
        self.profiles_dir = profiles_dir or PROFILES_DIR
        self.profiles = {}
        self.default_profile_name = "pre_1931"
        self._load_defaults()
        self._load_profiles()

    def _load_defaults(self):
        if os.path.exists(DEFAULT_CONFIG):
            with open(DEFAULT_CONFIG) as f:
                cfg = yaml.safe_load(f)
            if cfg and "temporal" in cfg:
                self.default_profile_name = cfg["temporal"].get("default_profile", "pre_1931")

    def _load_profiles(self):
        if not os.path.isdir(self.profiles_dir):
            return
        for fname in sorted(os.listdir(self.profiles_dir)):
            if fname.endswith((".yaml", ".yml")):
                path = os.path.join(self.profiles_dir, fname)
                try:
                    with open(path) as f:
                        data = yaml.safe_load(f)
                    if data and "name" in data:
                        self.profiles[data["name"]] = TemporalProfile(data)
                except Exception as e:
                    pass

    def get(self, name):
        return self.profiles.get(name)

    def get_default(self):
        return self.profiles.get(self.default_profile_name) or next(iter(self.profiles.values()))

    def list_profiles(self):
        return [p.to_dict() for p in self.profiles.values()]

    def reload(self):
        self.profiles.clear()
        self._load_defaults()
        self._load_profiles()

    def create_profile(self, data):
        profile = TemporalProfile(data)
        path = os.path.join(self.profiles_dir, f"{data['name']}.yaml")
        import yaml as yml
        with open(path, "w") as f:
            yml.dump(data, f, default_flow_style=False)
        self.profiles[data["name"]] = profile
        return profile
