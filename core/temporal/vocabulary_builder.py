"""Derives era-specific forbidden concepts from cutoff date.
Alternative vocabulary generation using milestone-based approach."""

from datetime import date

_MILESTONES = [
    (2020, "mRNA vaccine"),
    (2016, "tiktok", "TikTok"),
    (2010, "instagram", "Instagram"),
    (2009, "uber", "Uber"),
    (2008, "cryptocurrency", "blockchain", "bitcoin"),
    (2007, "iphone", "iPhone"),
    (2005, "youtube", "YouTube"),
    (2004, "facebook", "Facebook"),
    (2004, "podcast"),
    (2001, "wikipedia", "Wikipedia"),
    (2001, "war on terror"),
    (1998, "google", "Google"),
    (1997, "social media", "WiFi"),
    (1996, "cloud computing", "USB"),
    (1995, "streaming"),
    (1992, "smartphone"),
    (1991, "world wide web", "SSD"),
    (1989, "cybersecurity"),
    (1986, "self-driving", "genome"),
    (1984, "flash memory"),
    (1981, "nanotechnology"),
    (1975, "personal computer", "climate change", "global warming"),
    (1973, "GPS", "genetic engineering", "cell phone", "mobile phone"),
    (1972, "space shuttle"),
    (1971, "microprocessor", "email"),
    (1969, "internet"),
    (1968, "virtual reality"),
    (1960, "laser", "operating system"),
    (1959, "machine learning"),
    (1958, "integrated circuit", "NASA", "software"),
    (1957, "satellite", "Sputnik"),
    (1956, "AI", "artificial intelligence"),
    (1954, "solar panel"),
    (1953, "DNA"),
    (1947, "transistor", "Cold War"),
    (1945, "computer", "nuclear weapon", "nuclear bomb", "atomic bomb"),
    (1939, "WWII", "World War II"),
    (1903, "airplane"),
    (1897, "electron"),
    (1896, "radio"),
    (1895, "cinema", "x-ray"),
    (1886, "automobile"),
    (1876, "telephone"),
]


class VocabularyBuilder:
    def __init__(self, cutoff_date):
        self.cutoff_year = cutoff_date.year

    def build_forbidden_terms(self, buffer_years=0):
        terms = []
        for milestone in _MILESTONES:
            year = milestone[0]
            if year > self.cutoff_year + buffer_years:
                for concept in milestone[1:]:
                    terms.append(concept)
        return terms

    @staticmethod
    def get_milestones_for_era(cutoff_year):
        return [m for m in _MILESTONES if m[0] <= cutoff_year]
