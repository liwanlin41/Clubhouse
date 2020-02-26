import matplotlib.pyplot as plt, mpld3
import datetime as dt
from .db import *

def plot(time_range, data_format, club_id = None, member_id = None):
    if club_id == None:
        rows = get_all_checkins()
    elif member_id == None:
        rows = get_checkins_by_clubhouse(club_id)
    else:
        rows = get_checkins_by_member(club_id, member_id)

    if data_format == '0':
        return plot_checkins(time_range, rows)
    elif data_format == '1':
        return plot_timeofday(time_range, rows)
    elif data_format == '2':
        return plot_dayofweek(time_range, rows)
    elif data_format == '3':
        return avg_stats(time_range, rows)
    elif data_format == '4':
        return plot_nummembers(club_id)

def plot_checkins(time_range, rows):
    fig, ax = plt.subplots()

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
    points = ax.plot_date(keys, values, xdate=True)
    ax.plot_date(keys, values, 'b-', xdate=True)
    ax.set_xlim([current_group - delta[time_range], current_group])
    ax.set_ylim([0, max_y+2])
    if time_range == '1':
        ax.set_title('Checkins Per Hour')
    else:
        ax.set_title('Checkins Per Day')
    tooltip = mpld3.plugins.PointLabelTooltip(points[0], values)
    mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)

def plot_timeofday(time_range, rows):
    fig, ax = plt.subplots()

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
    points = ax.plot_date(datetimes, values, xdate=True)
    ax.plot_date(datetimes, values, 'b-', xdate=True)
    ax.set_xlim([start_time, start_time + dt.timedelta(hours=23)])
    ax.set_ylim([0, max_y+2])
    ax.set_title('Checkins By Hour of the Day')
    tooltip = mpld3.plugins.PointLabelTooltip(points[0], values)
    mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)

def plot_dayofweek(time_range, rows):
    fig, ax = plt.subplots()

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
    ax.set_title('Checkins By Day of the Week')
    for i in range(7):
        label = ['<div> ' + str(timecounts[i]) + '</div>']
        tooltip = mpld3.plugins.PointHTMLTooltip(boxes[i], label, hoffset=15, voffset=-15)
        mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)

def avg_stats(time_range, rows):
    current_time = dt.datetime.now()

    delta = {'1': dt.timedelta(hours=24), '7': dt.timedelta(days=7), '30': dt.timedelta(days=30), '365': dt.timedelta(days=365)}

    num_days = int(time_range)
    num_checkins = 0
    num_hours = 0

    for (member_id, checkin, checkout, clubhouse_id) in rows:
        if checkin < current_time - delta[time_range]:
            continue
        num_checkins = num_checkins + 1
        if checkout == None:
            checkout = dt.datetime.now()
        num_hours = num_hours + round((checkout - checkin).total_seconds() / 3600, 2)
    return '<div> Average Number of Checkins Per Day: ' + str(round(num_checkins / num_days, 2)) + '</div><br><div> Average Number of Hours Stayed Per Checkin: ' + str(round(num_hours / num_checkins, 2)) + '</div>'

def plot_nummembers(club_id):
    fig, ax = plt.subplots()

    if club_id == None:
        rows = get_all_joindates()
    else:
        rows = get_clubhouse_member_joindates(club_id)
    
    timecounts = {}
    current_count = 0

    for (member_id, join_date) in rows:
        if join_date == None:
            continue
        join_date = dt.datetime(join_date.year, join_date.month, join_date.day)
        if current_count == 0:
            timecounts[join_date - dt.timedelta(days=1)] = 0
        current_count = current_count + 1
        timecounts[join_date] = current_count

    keys, values = zip(*timecounts.items())
    points = ax.plot_date(keys, values, xdate=True)
    ax.plot_date(keys, values, 'b-', xdate=True)
    ax.set_ylim([0, current_count + 10])
    ax.set_title('Number of Members Over Time')
    tooltip = mpld3.plugins.PointLabelTooltip(points[0], values)
    mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)

def plot_by_member(club_id, member_id, time_range):
    fig, ax = plt.subplots()

    rows = get_checkins_by_member(club_id, member_id)
    current_day = dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = dt.timedelta(days=time_range)

    timecounts = {}
    for i in range(time_range + 1):
        timecounts[current_day - dt.timedelta(days=i)] = 0
    max_y = 0

    for (member_id, checkin, checkout, clubhouse_id) in rows:
        if checkin < current_day - delta:
            continue
        if checkout == None:
            checkout = dt.datetime.now()
        checkin_day = checkin.replace(hour=0, minute=0, second=0, microsecond=0)
        timecounts[checkin_day] = timecounts[checkin_day] + round((checkout - checkin).total_seconds() / 3600, 2)
        max_y = max(max_y, timecounts[checkin_day])

    try:
        keys, values = zip(*timecounts.items())
    except ValueError:
        return 'No checkins by this member'
    points = ax.plot_date(keys, values, xdate=True)
    ax.plot_date(keys, values, 'b-', xdate=True)
    ax.set_xlim([current_day - delta, current_day])
    ax.set_ylim([0, max_y+10])
    ax.set_title('Hours Spent Per Day')
    tooltip = mpld3.plugins.PointLabelTooltip(points[0], values)
    mpld3.plugins.connect(fig, tooltip)
    return mpld3.fig_to_html(fig)
