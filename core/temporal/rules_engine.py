"""Dynamically generates forbidden concepts based on cutoff_date."""

from datetime import date

_ERAS = [
    (1800, "Enlightenment / Regency"),
    (1837, "Victorian"),
    (1901, "Edwardian / Early Modern"),
    (1914, "Pre-WWI"),
    (1918, "Interwar"),
    (1939, "WWII Era"),
    (1945, "Post-War / Mid-Century"),
    (1960, "Space Age / Cold War"),
    (1980, "Late Cold War / Early Digital"),
    (1990, "Pre-Internet"),
    (1995, "Early Internet"),
    (2005, "Modern Digital"),
    (2010, "Contemporary"),
]

_CONCEPT_ERA = {
    "transistor": 1947,
    "integrated circuit": 1958,
    "microprocessor": 1971,
    "personal computer": 1975,
    "internet": 1969,
    "world wide web": 1989,
    "email": 1971,
    "smartphone": 1992,
    "cell phone": 1973,
    "mobile phone": 1973,
    "AI": 1956,
    "artificial intelligence": 1956,
    "machine learning": 1959,
    "deep learning": 2006,
    "computer": 1945,
    "laser": 1960,
    "satellite": 1957,
    "Sputnik": 1957,
    "spacecraft": 1957,
    "NASA": 1958,
    "Apollo": 1961,
    "space shuttle": 1972,
    "GPS": 1973,
    "DNA": 1953,
    "genetic engineering": 1973,
    "cloning": 1952,
    "nuclear weapon": 1945,
    "nuclear bomb": 1945,
    "atomic bomb": 1945,
    "WWII": 1939,
    "World War II": 1939,
    "Cold War": 1947,
    "social media": 1997,
    "cryptocurrency": 2008,
    "blockchain": 2008,
    "nanotechnology": 1981,
    "climate change": 1975,
    "global warming": 1975,
    "virtual reality": 1968,
    "self-driving": 1986,
    "cloud computing": 1996,
    "USB": 1996,
    "WiFi": 1997,
    "SSD": 1991,
    "streaming": 1995,
    "podcast": 2004,
    "wikipedia": 2001,
    "google": 1998,
    "war on terror": 2001,
    "cybersecurity": 1989,
    "deepfake": 2017,
    "gig economy": 2008,
    "radio": 1895,
    "television": 1927,
    "airplane": 1903,
    "electron": 1897,
    "quantum mechanics": 1900,
    "radioactivity": 1896,
    "cinema": 1895,
    "x-ray": 1895,
    "telephone": 1876,
    "automobile": 1886,
}


class RulesEngine:
    def __init__(self, cutoff_date, strictness="medium"):
        self.cutoff_date = cutoff_date
        self.cutoff_year = cutoff_date.year
        self.strictness_mult = {"low": 0.3, "medium": 0.6, "high": 1.0}.get(strictness, 0.6)

    def generate_forbidden_terms(self):
        terms = []
        year_cut = self.cutoff_year
        strict_mult = self.strictness_mult

        base_offset = int(5 * (1 - strict_mult))
        effective_year = year_cut + base_offset

        for concept, earliest in _CONCEPT_ERA.items():
            if earliest >= effective_year:
                terms.append(concept)

        if strict_mult >= 0.6:
            for concept, earliest in _CONCEPT_ERA.items():
                if earliest >= year_cut - 10 and earliest < effective_year:
                    terms.append(concept)

        buffer_years = 0 if strict_mult >= 0.8 else 5 if strict_mult >= 0.4 else 10
        if 1900 >= year_cut - buffer_years:
            terms.append("19[0-9][0-9]")
        if 2000 >= year_cut - buffer_years:
            terms.append("20[0-9][0-9]")

        seen = set()
        deduped = []
        for t in terms:
            key = t.lower().strip()
            if key not in seen:
                seen.add(key)
                deduped.append(t)
        return deduped

    def infer_era_style(self):
        for start_year, label in reversed(_ERAS):
            if self.cutoff_year >= start_year:
                return label
        return "Pre-Modern"

    def get_allowed_domains(self):
        if self.cutoff_year < 1850:
            return ["natural philosophy", "Newtonian physics", "steam power",
                    "mechanical engineering", "classical chemistry"]
        elif self.cutoff_year < 1900:
            return ["19th century science", "industrial engineering", "telegraphy"]
        elif self.cutoff_year < 1950:
            return ["classical/early quantum physics", "industrial engineering",
                    "vacuum tube electronics"]
        elif self.cutoff_year < 1990:
            return ["modern physics", "early computing", "space age technology"]
        else:
            return ["contemporary science", "digital computing", "modern engineering"]
