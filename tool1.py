from datetime import datetime

from flask import render_template, request, redirect, url_for, session
import matplotlib

from utils import calculate_blocks, adjust_blocks
from utils import create_sleep_impact_graph

# Set backend for matplotlib
matplotlib.use('Agg')


class SleepImpactGraph:
    def create_graph(self, blocks):
        return create_sleep_impact_graph(blocks)


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
