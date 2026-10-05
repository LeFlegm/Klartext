import re
from datetime import date

# Month names in the Swiss national languages plus English (casefolded).
MONTHS = {
    # French
    "janvier": 1, "février": 2, "fevrier": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
    "juillet": 7, "août": 8, "aout": 8, "septembre": 9, "octobre": 10, "novembre": 11,
    "décembre": 12, "decembre": 12,
    # German
    "januar": 1, "jänner": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "juni": 6,
    "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12,
    # Italian
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4, "maggio": 5, "giugno": 6,
    "luglio": 7, "agosto": 8, "settembre": 9, "ottobre": 10, "dicembre": 12,
    # English
    "january": 1, "february": 2, "march": 3, "may": 5, "june": 6, "july": 7,
    "october": 10, "december": 12,
}

# "31 octobre 2026", "1er novembre 2026", "15. November 2026"
_TEXT_DATE = re.compile(r"\b(\d{1,2})(?:er|\.)?\s+(\w+)\s+(\d{4})\b")
# "31.10.2026", "31/10/2026"
_NUMERIC_DATE = re.compile(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b")
# "2026-10-31"
_ISO_DATE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")

def _safe_date(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None

def find_dates(text: str) -> set[date]:
    """Return every calendar date written in the text, in any supported format."""
    text = re.sub(r"\s+", " ", text).casefold()
    found: set[date | None] = set()

    for day, month_name,year in _TEXT_DATE.findall(text):
        month = MONTHS.get(month_name)
        if month is not None:
            found.add(_safe_date(int(year), month, int(day)))
    for day, month, year in _NUMERIC_DATE.findall(text):
        found.add(_safe_date(int(year), int(month), int(day)))
    for year, month, day in _ISO_DATE.findall(text):
        found.add(_safe_date(int(year), int(month), int(day)))

    found.discard(None)
    return found