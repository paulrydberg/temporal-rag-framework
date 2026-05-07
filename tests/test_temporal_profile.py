import pytest
from app.temporal_profile import TemporalProfile, ProfileRegistry
from app.prompt_builder import build_prompt


class TestTemporalProfile:
    def test_load_pre1931(self):
        reg = ProfileRegistry()
        p = reg.get("pre_1931")
        assert p is not None
        assert p.cutoff_year == 1931
        assert len(p.forbidden_terms) > 0

    def test_load_all_profiles(self):
        reg = ProfileRegistry()
        assert len(reg.profiles) >= 5

    def test_check_violation(self):
        p = TemporalProfile({"forbidden_terms": ["AI", "internet"]})
        assert p.check("This AI system is modern") == "AI"
        assert p.check("This is fine") is None

    def test_check_all_multiple(self):
        p = TemporalProfile({"forbidden_terms": ["computer", "internet"]})
        v = p.check_all("The computer uses the internet")
        assert len(v) == 2

    def test_format_system_prompt(self):
        p = TemporalProfile({"name": "test", "cutoff_year": 1931, "system_prompt": "Knowledge cutoff: {CUTOFF_YEAR}"})
        prompt = p.format_system_prompt(2026)
        assert "1931" in prompt
        assert "2026" not in prompt

    def test_to_dict(self):
        p = TemporalProfile({"name": "test", "cutoff_year": 1900})
        d = p.to_dict()
        assert d["name"] == "test"
        assert d["cutoff_year"] == 1900

    def test_build_prompt(self):
        reg = ProfileRegistry()
        p = reg.get_default()
        prompt = build_prompt("Explain steam engines", p)
        assert "Explain steam engines" in prompt
        assert str(p.cutoff_year) in prompt or "1931" in prompt

    def test_build_prompt_with_rag(self):
        reg = ProfileRegistry()
        p = reg.get_default()
        prompt = build_prompt("Explain trains", p, rag_context=["Steam locomotives were invented in 1804"])
        assert "Steam locomotives" in prompt

    def test_profile_create_roundtrip(self):
        import tempfile, os
        tmpdir = tempfile.mkdtemp()
        reg = ProfileRegistry(profiles_dir=tmpdir)
        data = {"name": "test_era", "cutoff_year": 1950, "forbidden_terms": ["AI"]}
        reg.create_profile(data)
        assert reg.get("test_era") is not None
        assert reg.get("test_era").cutoff_year == 1950
        assert reg.get("test_era").check("AI is cool") == "AI"
