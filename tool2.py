from datetime import datetime
import base64
import io

from flask import render_template, request, redirect, url_for, session
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from utils import calculate_blocks, adjust_blocks
from constants import RED_COLOR, YELLOW_COLOR, GREEN_COLOR, GREY_COLOR

# Set backend for matplotlib
matplotlib.use('Agg')


class SleepImpactGraph:
    """
    Class to create the sleep impact graph based on light exposure and day number.
    """

    def create_graph(self, blocks, day_number=None):
        rect_height = 5
        figure, axis = plt.subplots()
        axis.fill_between([0, 24], 0, rect_height, color=GREY_COLOR)
        for color, (start, end) in blocks:
            axis.fill_between([start, end if end != 24 else 24], 0, rect_height, color=color)
        axis.set_xlabel('')
        axis.set_ylim(0, 10)
        axis.tick_params(axis='y', colors='white')

        wake_time_hours = blocks[2][1][0]
        wake_time_minutes = (wake_time_hours % 1) * 60
        wake_time_formatted = f'{int(wake_time_hours)}:{int(wake_time_minutes):02}'

        x_ticks = np.arange(0, 25, 2)
        x_labels = [f'{x}h' for x in x_ticks]
        plt.xticks(x_ticks, x_labels)

        # Using predefined color constants for patches
        red_patch = plt.Line2D([], [], color=RED_COLOR, label='Wake up later')
        yellow_patch = plt.Line2D([], [], color=YELLOW_COLOR, label='Wake up sooner')
        green_patch = plt.Line2D([], [], color=GREEN_COLOR, label='Maintain schedule')
        grey_patch = plt.Line2D([], [], color=GREY_COLOR, label='Dead zone')
        wake_up_patch = plt.Line2D([], [], color='none', label=f'Wake-up Time: {wake_time_formatted}')
        axis.legend(handles=[red_patch, yellow_patch, green_patch, grey_patch, wake_up_patch], loc='upper right')
        axis.grid(True)

        if day_number is not None:
            plt.title(f'Day {day_number}')
        else:
            plt.title('How and when light exposure affects your wake up time')

        figfile = io.BytesIO()
        plt.savefig(figfile, format='png')
        img_data = base64.b64encode(figfile.getvalue()).decode('utf8')
        return img_data


def handle_all_nighter(desired_wake_time):
    wake_time_dt = datetime.strptime(desired_wake_time, '%H:%M')
    wake_time_hours = wake_time_dt.hour + wake_time_dt.minute / 60
    blocks = calculate_blocks(wake_time_hours)
    adjusted_blocks = adjust_blocks(blocks)
    graph = SleepImpactGraph()
    img_data = graph.create_graph(adjusted_blocks)
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
