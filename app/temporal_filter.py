"""Temporal filter — validates output against pre-1931 constraints."""

import re


class TemporalFilter:
    FORBIDDEN_TERMS = [
        r"\bAI\b", r"\bartificial intelligence", r"\bneural network",
        r"\bdeep learning", r"\bmachine learning",
        r"\bcomputer\b", r"\binternet\b", r"\bwww\b", r"\bwebsite\b",
        r"\bemail\b", r"\bsmartphone\b", r"\bcell phone\b", r"\bmobile phone\b",
        r"\btransistor\b", r"\bmicrochip\b", r"\bsemiconductor\b", r"\bintegrated circuit\b",
        r"\bquantum\b", r"\bdigital computer\b",
        r"\bnuclear weapon\b", r"\bnuclear bomb\b", r"\batomic bomb\b",
        r"\bGPS\b", r"\bsatellite\b", r"\bspacecraft\b",
        r"\bgenome\b", r"\bDNA\b", r"\bgenetic engineering\b",
        r"\blaser\b",
        r"\bsocial media\b",
        r"\bself-driving\b", r"\bautonomous vehicle\b",
        r"\bclimate change\b", r"\bglobal warming\b",
        r"\bworld wide web\b",
        r"\bnanotechnology\b",
        r"\brenewable energy\b", r"\bsolar panel\b",
        r"\bvirtual reality\b", r"\baugmented reality\b",
        r"\bcryptocurrency\b", r"\bblockchain\b",
        r"\bsoftware\b",
        r"\boperating system\b",
        r"\bNASA\b", r"\bSputnik\b", r"\bApollo\b",
        r"\bWWII\b", r"\bWorld War II\b", r"\bWorld War 2\b",
        r"\bCold War\b",
        r"\b198[0-9]\b", r"\b199[0-9]\b", r"\b20[0-9][0-9]\b",
    ]

    def __init__(self):
        self.patterns = [re.compile(t, re.IGNORECASE) for t in self.FORBIDDEN_TERMS]

    def check(self, text: str) -> str | None:
        for p in self.patterns:
            m = p.search(text)
            if m:
                return m.group(0)
        return None

    def check_all(self, text: str) -> list[str]:
        violations = []
        for p in self.patterns:
            m = p.search(text)
            if m:
                violations.append(m.group(0))
        return violations
