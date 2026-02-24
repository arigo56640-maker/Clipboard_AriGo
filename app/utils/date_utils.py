"""פורמט תאריכים בעברית — זמן יחסי ותצוגת תאריך."""

from datetime import datetime

from app.constants import STRINGS


def relative_time(timestamp_str) -> str:
    """המרת timestamp לזמן יחסי בעברית (לפני X דקות וכו')."""
    if not timestamp_str:
        return ""
    try:
        ts = datetime.fromisoformat(timestamp_str)
    except ValueError:
        return timestamp_str

    now = datetime.now()
    diff = now - ts
    seconds = int(diff.total_seconds())

    if seconds < 5:
        return STRINGS["ago_now"]
    if seconds < 60:
        return STRINGS["ago_seconds"].format(n=seconds)
    minutes = seconds // 60
    if minutes == 1:
        return STRINGS["ago_minute"]
    if minutes < 60:
        return STRINGS["ago_minutes"].format(n=minutes)
    hours = minutes // 60
    if hours == 1:
        return STRINGS["ago_hour"]
    if hours < 24:
        return STRINGS["ago_hours"].format(n=hours)
    days = diff.days
    if days == 1:
        return STRINGS["ago_yesterday"]
    if days < 7:
        return STRINGS["ago_days"].format(n=days)
    weeks = days // 7
    if weeks < 4:
        return STRINGS["ago_weeks"].format(n=weeks)
    months = days // 30
    if months == 1:
        return STRINGS["ago_month"]
    if months < 12:
        return STRINGS["ago_months"].format(n=months)
    years = days // 365
    if years == 1:
        return STRINGS["ago_year"]
    return STRINGS["ago_years"].format(n=years)


def format_date(timestamp_str) -> str:
    """תצוגת תאריך מלא."""
    if not timestamp_str:
        return ""
    try:
        ts = datetime.fromisoformat(timestamp_str)
        return ts.strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return timestamp_str
