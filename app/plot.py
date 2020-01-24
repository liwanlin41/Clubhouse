import matplotlib.pyplot as plt, mpld3
import datetime as dt
from .db import *

def plot(time_range, data_format):
    if data_format == '0':
        return plot_checkins(time_range)
    elif data_format == '1':
        return plot_timeofday(time_range)
    elif data_format == '2':
        return plot_dayofweek(time_range)

def plot_checkins(time_range):
    fig, ax = plt.subplots()

    rows = get_all_checkins()
    current_time = dt.datetime.now()

    delta = {'1': dt.timedelta(hours=24), '7': dt.timedelta(days=7), '30': dt.timedelta(days=30), '365': dt.timedelta(days=365)}

    timecounts = {}
    if time_range == '1':
        current_group = current_time.replace(minute=0, second=0, microsecond=0)
        for i in range(25):
            timecounts[current_group - dt.timedelta(hours=i)] = 0
    else:
        current_group = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(int(time_range)+1):
            timecounts[current_group - dt.timedelta(days=i)] = 0

    max_y = 0

    for (member_id, checkin, checkout, clubhouse_id) in rows:
        if checkin < current_time - delta[time_range]:
            continue
        checkin_group = checkin.replace(minute=0, second=0, microsecond=0)
        if time_range != '1':
            checkin_group = checkin_group.replace(hour=0)
        if checkin_group in timecounts.keys():
            timecounts[checkin_group] = timecounts[checkin_group] + 1
            max_y = max(max_y, timecounts[checkin_group])  

    try:
        keys, values = zip(*timecounts.items())
    except ValueError:
        return 'No checkins in this time range'
    ax.plot_date(keys, values, 'b-', xdate=True)
    ax.set_xlim([current_group - delta[time_range], current_group])
    ax.set_ylim([0, max_y])
    return mpld3.fig_to_html(fig)

def plot_timeofday(time_range):
    fig, ax = plt.subplots()

    rows = get_all_checkins()
    current_time = dt.datetime.now()
    start_time = current_time.replace(hour=0, minute=30, second=0, microsecond=0)

    delta = {'1': dt.timedelta(hours=24), '7': dt.timedelta(days=7), '30': dt.timedelta(days=30), '365': dt.timedelta(days=365)}

    timecounts = {}
    for i in range(24):
        timecounts[i] = 0

    max_y = 0

    for (member_id, checkin, checkout, clubhouse_id) in rows:
        if checkin < current_time - delta[time_range]:
            continue 
        timecounts[checkin.hour] = timecounts[checkin.hour] + 1
        max_y = max(max_y, timecounts[checkin.hour])  

    try:
        keys, values = zip(*timecounts.items())
    except ValueError:
        return 'No checkins in this time range'
    datetimes = [current_time.replace(hour=item, minute=30, second=0, microsecond=0) for item in keys]
    points = ax.plot_date(datetimes, values, 'b-', xdate=True)
    ax.set_xlim([start_time, start_time + dt.timedelta(hours=23)])
    ax.set_ylim([0, max_y])
    return mpld3.fig_to_html(fig)

def plot_dayofweek(time_range):
    fig, ax = plt.subplots()

    rows = get_all_checkins()
    current_time = dt.datetime.now()

    delta = {'1': dt.timedelta(hours=24), '7': dt.timedelta(days=7), '30': dt.timedelta(days=30), '365': dt.timedelta(days=365)}

    timecounts = [0, 0, 0, 0, 0, 0, 0]
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    x = [0, 1, 2, 3, 4, 5, 6]
    max_y = 0

    for (member_id, checkin, checkout, clubhouse_id) in rows:
        if checkin < current_time - delta[time_range]:
            continue
        timecounts[checkin.weekday()] = timecounts[checkin.weekday()] + 1
        max_y = max(max_y, timecounts[checkin.weekday()])

    boxes = ax.bar(x, timecounts)
    ax.set_xticks(x)
    ax.set_xticklabels(days)
    for i in range(7):
        label = ['<div> ' + str(timecounts[i]) + '</div>']
        tooltip = mpld3.plugins.PointHTMLTooltip(boxes[i], label, hoffset=15, voffset=-15)
        mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)
