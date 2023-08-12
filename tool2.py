from datetime import datetime
from flask import render_template, request, redirect, url_for, session
import matplotlib
from utils import calculate_blocks, adjust_blocks
from utils import create_sleep_impact_graph

# Set backend for matplotlib
matplotlib.use('Agg')


class SleepImpactGraph:
    def create_graph(self, blocks, day_number):
        return create_sleep_impact_graph(blocks, day_number)


def handle_all_nighter(desired_wake_time):
    wake_time_dt = datetime.strptime(desired_wake_time, '%H:%M')
    wake_time_hours = wake_time_dt.hour + wake_time_dt.minute / 60
    blocks = calculate_blocks(wake_time_hours)
    adjusted_blocks = adjust_blocks(blocks)
    graph = SleepImpactGraph()
    img_data = graph.create_graph(adjusted_blocks, day_number=1)
    return img_data


def handle_gradual_shift(current_wake_time, desired_wake_time, days_for_shift):
    current_wake_time_dt = datetime.strptime(current_wake_time, '%H:%M')
    current_wake_time_hours = current_wake_time_dt.hour + current_wake_time_dt.minute / 60
    desired_wake_time_dt = datetime.strptime(desired_wake_time, '%H:%M')
    desired_wake_time_hours = desired_wake_time_dt.hour + desired_wake_time_dt.minute / 60
    delta_wake_time_hours = (desired_wake_time_hours - current_wake_time_hours) / days_for_shift
    img_data_list = []
    graph = SleepImpactGraph()

    for day in range(days_for_shift + 1):
        wake_time_hours = current_wake_time_hours + delta_wake_time_hours * day
        blocks = calculate_blocks(wake_time_hours)
        adjusted_blocks = adjust_blocks(blocks)
        img_data = graph.create_graph(adjusted_blocks, day_number=day + 1)
        img_data_list.append(img_data)

    return img_data_list


def tool2_home():
    img_data = session.pop('img_data', [])
    graph_generated = bool(img_data)
    return render_template('switch_wake_time.html', img_data=img_data, graph_generated=graph_generated)


def tool2_submit():
    current_wake_time = request.form['currentWakeTime']
    desired_wake_time = request.form['desiredWakeTime']
    shift_method = request.form['shiftMethod']

    if shift_method == 'allNighter':
        img_data = [handle_all_nighter(desired_wake_time)]
    else:
        days_for_shift = int(request.form['daysForShift'])
        img_data = handle_gradual_shift(current_wake_time, desired_wake_time, days_for_shift)

    session['img_data'] = img_data
    return redirect(url_for('tool2_home'))
