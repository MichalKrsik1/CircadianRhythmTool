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
    Class to create the sleep impact graph based on light exposure
    """

    @staticmethod
    def create_graph(blocks):
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

        red_patch = plt.Line2D([], [], color=RED_COLOR, label='Wake up later')
        yellow_patch = plt.Line2D([], [], color=YELLOW_COLOR, label='Wake up sooner')
        green_patch = plt.Line2D([], [], color=GREEN_COLOR, label='Maintain schedule')
        grey_patch = plt.Line2D([], [], color=GREY_COLOR, label='Dead zone')
        wake_up_patch = plt.Line2D([], [], color='none', label=f'Wake-up Time: {wake_time_formatted}')
        axis.legend(handles=[red_patch, yellow_patch, green_patch, grey_patch, wake_up_patch], loc='upper right')

        axis.grid(True)
        plt.title('How and when light exposure affects your wake up time')

        figfile = io.BytesIO()
        plt.savefig(figfile, format='png')

        img_data = base64.b64encode(figfile.getvalue()).decode('utf8')
        return img_data


def tool1_home():
    img_data = session.pop('img_data', None)
    return render_template('light_on_sleep_impact.html', img_data=img_data)


def tool1_submit():
    try:
        wake_time = request.form['wakeTime']
        wake_time_dt = datetime.strptime(wake_time, '%H:%M')
        wake_time_hours = wake_time_dt.hour + wake_time_dt.minute / 60

        blocks = calculate_blocks(wake_time_hours)
        adjusted_blocks = adjust_blocks(blocks)

        graph = SleepImpactGraph()
        graph_image_data = graph.create_graph(adjusted_blocks)
        session['img_data'] = graph_image_data

        return redirect(url_for('tool1_home'))
    except ValueError:  # Handle time format errors
        return "Invalid wake time format. Please use HH:MM.", 400
