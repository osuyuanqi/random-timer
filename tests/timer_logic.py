import random
from datetime import date

# ── Max-minutes logic ─────────────────────────────────────────────────────────

BASE_MINUTES  = 90       # default max in May 2026
BASE_YEAR     = 2026
BASE_MONTH    = 5        # May
STEP_PER_MONTH = 30      # +30 min each calendar month


def calc_default_max(for_date: date | None = None) -> int:
    """
    Return the default max duration (minutes) for a given date.
    Starts at 90 in May 2026 and increases by 30 every month.
    """
    if for_date is None:
        for_date = date.today()

    months_elapsed = (
        (for_date.year - BASE_YEAR) * 12
        + (for_date.month - BASE_MONTH)
    )
    return BASE_MINUTES + max(0, months_elapsed) * STEP_PER_MONTH


# ── Timer helpers ─────────────────────────────────────────────────────────────

def get_random_session_minutes() -> int:
    """
    New helper to mirror the sliderless logic:
    Calculates dynamic max for today and rolls a surprise value.
    """
    dynamic_max = calc_default_max()
    return random.randint(1, dynamic_max)


def random_minutes(max_minutes: int) -> int:
    """Return a random integer in [1, max_minutes]."""
    if max_minutes < 1:
        raise ValueError(f"max_minutes must be >= 1, got {max_minutes}")
    return random.randint(1, max_minutes)


def format_time(seconds: int) -> str:
    """
    Convert total seconds to HH:MM:SS string.

    >>> format_time(5400)
    '01:30:00'
    """
    if seconds < 0:
        raise ValueError("Negative time")

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:02}"


def is_urgent(remaining: int, threshold: int = 30) -> bool:
    """Return True when 0 < remaining <= threshold."""
    return 0 < remaining <= threshold


def progress_fraction(remaining: int, total: int) -> float:
    """Return remaining/total clamped to [0.0, 1.0]."""
    if total <= 0:
        raise ValueError(f"total must be positive, got {total}")
    return max(0.0, min(1.0, remaining / total))


# ── Session / database helpers ────────────────────────────────────────────────

def aggregate_day(timers: list[int]) -> dict:
    """Build a day-record for Firestore."""
    return {
        "timers": timers[:],
        "total":  sum(timers),
    }


def monthly_total(sessions: list[dict], year: int, month: int) -> int:
    """Sum the 'total' field for all sessions in a month."""
    prefix = f"{year:04d}-{month:02d}"
    return sum(s["total"] for s in sessions if s.get("date", "").startswith(prefix))
