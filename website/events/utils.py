from datetime import datetime, date, timedelta


def today_midnight():
    return datetime.combine(date.today(), datetime.min.time())


def week_n(event_date: datetime):
    today = today_midnight()
    week_start = today - timedelta(days=today.weekday())
    days_between = (event_date - week_start).days
    return days_between // 7
