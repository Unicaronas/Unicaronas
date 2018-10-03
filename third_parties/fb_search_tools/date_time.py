import re
from datetime import timedelta, datetime
from django.utils import timezone


WEEKDAY_LIST = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']


def find_typed_date(message):
    date = re.findall(r"\d+/\d+", message)
    now = timezone.now()
    return f"{date[0]}/{now.year}" if date else None


def find_relative_date(item):
    created_time = item['created_time']
    message = item['message']

    # Easy ones (today, tomorrow, day after tomorrow)
    day_after_tomorrow = re.search(r'depois de amanha', message)
    if day_after_tomorrow:
        r_date = created_time + timedelta(days=2)
        return f"{r_date.day}/{r_date.month}/{r_date.year}"
    tomorrow = re.search(r'amanha', message)
    if tomorrow:
        r_date = created_time + timedelta(days=1)
        return f"{r_date.day}/{r_date.month}/{r_date.year}"
    today = re.search(r'hoje', message)
    if today:
        return f"{created_time.day}/{created_time.month}/{created_time.year}"

    created_weekday = created_time.weekday()

    # now search by weekday
    for i, weekday in enumerate(WEEKDAY_LIST):
        found = re.search(weekday, message)
        if found:
            days_apart = (i - created_weekday) % 7
            found_date = created_time + timedelta(days=days_apart)
            return f"{found_date.day}/{found_date.month}/{found_date.year}"
    # If none were found, return none
    return None


def find_date(item):
    """Finds date as %d/%m/%Y"""
    date = find_typed_date(item['message'])
    if date is None:
        date = find_relative_date(item)
    return date


def find_time(item):
    """finds time as %H:%M"""
    message = item['message']
    s1 = re.findall(r"\d+:\d+", message, re.I)
    s2 = re.findall(r"(\d+h\d+)", message, re.I)
    s3 = re.findall(r"(\d+(\s+)?h)", message, re.I)
    if s1:
        time = str(re.findall(r'\d+:\d+', str(s1[0]))[0])
    elif s2:
        time = str(re.findall(r'\d+h\d+', str(s2[0]), re.I)[0])
        r = re.compile(re.escape('h'), re.IGNORECASE)
        time = r.sub(':', time)
    elif s3:
        time = "%s:00" % str(re.findall(r'\d+', str(s3[0]))[0])
    else:
        time = None
    return time


def find_datetime(item):
    date = find_date(item)
    if date is None:
        return None
    time = find_time(item)
    if time is None:
        return None
    return datetime.strptime(f"{time} {date}", "%H:%M %d/%m/%Y")
