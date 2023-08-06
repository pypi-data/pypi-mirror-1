#!/usr/bin/env python
#countdown.py

from datetime import datetime
from sys import argv

def get_datetime(year, month, day, hour=0, minute=0, second=0):
    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

def get_timedelta(target):
    return target - datetime.now()

def get_delta_tuple(delta):
    day = delta.days
    s = delta.seconds
    hour = (s / 60) / 60
    min = (s / 60 ) % 60
    sec = s % 60
    return day, hour, min, sec

def format_delta_tuple(t):
    return '%s Day(s), %s Hour(s), %s Min(s), %s Sec(s)' % t

def countdown(*args):
    target = get_datetime(*args)
    delta = get_timedelta(target)
    t = get_delta_tuple(delta)
    return format_delta_tuple(t)

def main():
    args = argv
    args.pop(0)
    return countdown(*args)


if __name__ == '__main__':
    print main()


