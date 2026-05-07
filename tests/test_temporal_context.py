"""Tests for the cutoff-driven TemporalContext system."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.temporal import TemporalContext


class TestTemporalContext:
    def test_default_cutoff(self):
        ctx = TemporalContext()
        assert ctx.cutoff_year == 1931
        assert str(ctx.cutoff_date) == "1931-01-01"
        assert ctx.strictness == "medium"

    def test_specific_cutoff(self):
        ctx = TemporalContext("1965-06-01")
        assert ctx.cutoff_year == 1965
        assert str(ctx.cutoff_date) == "1965-06-01"

    def test_preset_name(self):
        ctx = TemporalContext("victorian")
        assert ctx.cutoff_year == 1901
        assert str(ctx.cutoff_date) == "1901-01-22"

    def test_all_presets(self):
        for name in TemporalContext.presets():
            ctx = TemporalContext(name)
            assert ctx.cutoff_year > 0

    def test_forbidden_terms_default(self):
        ctx = TemporalContext()
        terms = ctx.forbidden_terms
        assert len(terms) > 10
        # post-1931 concepts should be forbidden
        term_set = set(t.lower() for t in terms)
        assert "computer" in term_set or "digital computer" in term_set
        assert "AI" in term_set or "artificial intelligence" in term_set

    def test_forbidden_terms_1800(self):
        ctx = TemporalContext("1800-01-01")
        terms = ctx.forbidden_terms
        term_set = set(t.lower() for t in terms)
        assert "telephone" in term_set or "automobile" in term_set

    def test_forbidden_terms_2000(self):
        ctx = TemporalContext("2000-01-01")
        term_set = set(t.lower() for t in ctx.forbidden_terms)
        # post-2000 concepts should be forbidden
        assert "google" in term_set or "wikipedia" in term_set
        assert "cryptocurrency" in term_set

    def test_check_violation(self):
        ctx = TemporalContext()
        assert ctx.check("Uses AI technology") is not None
        assert ctx.check("Steam engines are powerful") is None

    def test_check_all_multiple(self):
        ctx = TemporalContext()
        v = ctx.check_all("The AI computer uses the internet")
        assert len(v) >= 2

    def test_system_prompt(self):
        ctx = TemporalContext("1900-01-01")
        sp = ctx.system_prompt
        assert "1900" in sp
        assert "time-bound" in sp

    def test_era_style(self):
        assert TemporalContext("1800-01-01").era_style == "Enlightenment / Regency"
        assert TemporalContext("1900-01-01").era_style == "Victorian"
        assert TemporalContext("1931-01-01").era_style == "Interwar"
        assert TemporalContext("1965-01-01").era_style == "Space Age / Cold War"
        assert TemporalContext("2000-01-01").era_style == "Early Internet"

    def test_to_dict(self):
        ctx = TemporalContext("1900-01-01", "high")
        d = ctx.to_dict()
        assert d["cutoff_year"] == 1900
        assert d["strictness"] == "high"

    def test_strictness_options(self):
        opts = TemporalContext.strictness_options()
        assert "low" in opts
        assert "medium" in opts
        assert "high" in opts

    def test_presets(self):
        p = TemporalContext.presets()
        assert "pre_1931" in p
        assert "victorian" in p
        assert p["pre_1931"]["cutoff_date"] == "1931-01-01"
