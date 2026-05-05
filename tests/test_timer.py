# test_timer.py
# Run with:  pytest test_timer.py -v
#
# Tests cover:
#   - Dynamic max-minutes calculation (month progression)
#   - Random minute generation
#   - Time formatting
#   - Urgent threshold detection
#   - Progress fraction
#   - Session aggregation & monthly totals

import pytest
from datetime import date
from timer_logic import (
    calc_default_max,
    random_minutes,
    format_time,
    is_urgent,
    progress_fraction,
    aggregate_day,
    monthly_total,
    BASE_MINUTES,
    STEP_PER_MONTH,
)


# ══════════════════════════════════════════════════════════════════════════════
# calc_default_max
# ══════════════════════════════════════════════════════════════════════════════

class TestCalcDefaultMax:
    def test_baseline_may_2026(self):
        assert calc_default_max(date(2026, 5, 1)) == 90

    def test_june_2025(self):
        assert calc_default_max(date(2026, 6, 1)) == 120

    def test_july_2025(self):
        assert calc_default_max(date(2026, 7, 15)) == 150

    def test_one_year_later_may_2026(self):
        # 12 months elapsed → 90 + 12*30 = 450
        assert calc_default_max(date(2027, 5, 1)) == 450

    def test_before_baseline_clamped(self):
        # Dates before May 2026 should not go below BASE_MINUTES
        assert calc_default_max(date(2025, 1, 1)) == BASE_MINUTES

    def test_exact_baseline_month_end(self):
        assert calc_default_max(date(2026, 5, 31)) == 90

    def test_step_size_is_30(self):
        v1 = calc_default_max(date(2026, 8, 1))
        v2 = calc_default_max(date(2026, 9, 1))
        assert v2 - v1 == STEP_PER_MONTH

    def test_returns_int(self):
        assert isinstance(calc_default_max(date(2026, 6, 1)), int)

    def test_monotonically_increasing(self):
        months = [date(2026, 5 + i if 5 + i <= 12 else 5 + i - 12,
                       1).replace(year=2026 if 5 + i <= 12 else 2027)
                  for i in range(6)]
        values = [calc_default_max(m) for m in months]
        assert values == sorted(values)


# ══════════════════════════════════════════════════════════════════════════════
# random_minutes
# ══════════════════════════════════════════════════════════════════════════════

class TestRandomMinutes:
    def test_within_range(self):
        for _ in range(300):
            result = random_minutes(90)
            assert 1 <= result <= 90

    def test_max_one_always_returns_one(self):
        for _ in range(50):
            assert random_minutes(1) == 1

    def test_distribution_covers_full_range(self):
        seen = set()
        for _ in range(1000):
            seen.add(random_minutes(10))
        assert seen == set(range(1, 11))

    def test_invalid_zero_raises(self):
        with pytest.raises(ValueError):
            random_minutes(0)

    def test_invalid_negative_raises(self):
        with pytest.raises(ValueError):
            random_minutes(-5)

    def test_returns_int(self):
        assert isinstance(random_minutes(90), int)

    def test_large_max(self):
        for _ in range(100):
            r = random_minutes(450)
            assert 1 <= r <= 450

    def test_respects_dynamic_monthly_limit(self):
        # If it's May 2026, max should be 90.
        # We test that 100 rolls never exceed that dynamic limit.
        dynamic_max = calc_default_max(date(2026, 5, 1)) # 90
        for _ in range(100):
            assert 1 <= random_minutes(dynamic_max) <= 90

    def test_respects_future_monthly_limit(self):
        # If it's June 2026, max should be 120.
        dynamic_max = calc_default_max(date(2026, 6, 1)) # 120
        results = [random_minutes(dynamic_max) for _ in range(200)]
        assert all(1 <= r <= 120 for r in results)
        assert any(r > 90 for r in results) # Check it actually uses the extra range

# ══════════════════════════════════════════════════════════════════════════════
# format_time
# ══════════════════════════════════════════════════════════════════════════════

class TestFormatTime:
    def test_zero(self):
        assert format_time(0) == "00:00:00"

    def test_one_second(self):
        assert format_time(1) == "00:00:01"

    def test_one_minute(self):
        assert format_time(60) == "00:01:00"

    def test_ninety_minutes(self):
        assert format_time(5400) == "01:30:00"

    def test_mixed(self):
        # 754 seconds is 12m 34s
        assert format_time(754) == "00:12:34"

    def test_leading_zeros_seconds(self):
        assert format_time(5) == "00:00:05"

    def test_format_structure(self):
        result = format_time(754)
        assert len(result) == 8
        assert result[2] == ":"
        assert result[5] == ":"


# ══════════════════════════════════════════════════════════════════════════════
# is_urgent
# ══════════════════════════════════════════════════════════════════════════════

class TestIsUrgent:
    def test_at_default_threshold(self):
        assert is_urgent(30) is True

    def test_below_threshold(self):
        assert is_urgent(1) is True

    def test_above_threshold(self):
        assert is_urgent(31) is False

    def test_zero_not_urgent(self):
        # 0 means finished, not in-progress urgent
        assert is_urgent(0) is False

    def test_custom_threshold(self):
        assert is_urgent(60, threshold=60) is True
        assert is_urgent(61, threshold=60) is False

    def test_negative_not_urgent(self):
        assert is_urgent(-1) is False


# ══════════════════════════════════════════════════════════════════════════════
# progress_fraction
# ══════════════════════════════════════════════════════════════════════════════

class TestProgressFraction:
    def test_full(self):
        assert progress_fraction(90 * 60, 90 * 60) == pytest.approx(1.0)

    def test_half(self):
        assert progress_fraction(45 * 60, 90 * 60) == pytest.approx(0.5)

    def test_empty(self):
        assert progress_fraction(0, 90 * 60) == pytest.approx(0.0)

    def test_clamped_above(self):
        assert progress_fraction(200, 100) == pytest.approx(1.0)

    def test_clamped_below(self):
        assert progress_fraction(-10, 100) == pytest.approx(0.0)

    def test_invalid_total_raises(self):
        with pytest.raises(ValueError):
            progress_fraction(30, 0)

    def test_returns_float(self):
        assert isinstance(progress_fraction(30, 60), float)


# ══════════════════════════════════════════════════════════════════════════════
# aggregate_day
# ══════════════════════════════════════════════════════════════════════════════

class TestAggregateDay:
    def test_single_timer(self):
        result = aggregate_day([45])
        assert result["timers"] == [45]
        assert result["total"] == 45

    def test_four_timers(self):
        result = aggregate_day([20, 35, 50, 25])
        assert result["total"] == 130
        assert len(result["timers"]) == 4

    def test_empty(self):
        result = aggregate_day([])
        assert result["total"] == 0
        assert result["timers"] == []

    def test_more_than_four_timers_all_stored(self):
        timers = [10, 20, 30, 40, 50]
        result = aggregate_day(timers)
        # All timers stored (Firestore has no hard limit at logic layer)
        assert result["timers"] == timers
        assert result["total"] == 150

    def test_does_not_mutate_input(self):
        original = [10, 20]
        aggregate_day(original)
        assert original == [10, 20]

    def test_total_matches_sum(self):
        timers = [7, 13, 22, 48]
        result = aggregate_day(timers)
        assert result["total"] == sum(timers)


# ══════════════════════════════════════════════════════════════════════════════
# monthly_total
# ══════════════════════════════════════════════════════════════════════════════

class TestMonthlyTotal:
    SESSIONS = [
        {"date": "2025-05-01", "total": 45},
        {"date": "2025-05-03", "total": 60},
        {"date": "2025-05-15", "total": 30},
        {"date": "2025-06-01", "total": 90},
        {"date": "2025-06-20", "total": 50},
        {"date": "2024-12-31", "total": 20},
    ]

    def test_may_2025(self):
        assert monthly_total(self.SESSIONS, 2025, 5) == 135

    def test_june_2025(self):
        assert monthly_total(self.SESSIONS, 2025, 6) == 140

    def test_month_with_no_data(self):
        assert monthly_total(self.SESSIONS, 2025, 7) == 0

    def test_different_year(self):
        assert monthly_total(self.SESSIONS, 2024, 12) == 20

    def test_empty_sessions(self):
        assert monthly_total([], 2025, 5) == 0

    def test_all_same_month(self):
        sessions = [{"date": "2025-05-0" + str(i), "total": 10} for i in range(1, 6)]
        assert monthly_total(sessions, 2025, 5) == 50
