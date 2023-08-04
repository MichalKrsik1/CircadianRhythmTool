from flask import Flask, render_template, request
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
matplotlib.use('Agg')

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    wake_time = request.form['wakeTime']
    wake_time_dt = datetime.strptime(wake_time, '%H:%M')
    wake_time_hours = wake_time_dt.hour + wake_time_dt.minute / 60

    tm = wake_time_hours - 2

    red_start = (tm - 4) % 24
    red_end = tm % 24
    red_block = ('#d7285c', (red_start, red_end))

    yellow_start = tm % 24
    yellow_end = wake_time_hours % 24
    yellow_block = ('#e5de1a', (yellow_start, yellow_end))

    green_start = wake_time_hours % 24
    green_end = (wake_time_hours + 4) % 24
    green_block = ('#44c53a', (green_start, green_end))

    blocks = [red_block, yellow_block, green_block]

    adjusted_blocks = []
    for color, (start, end) in blocks:
        if start > end:
            first_block = (color, (start, 24))
            second_block = (color, (0, end))
            adjusted_blocks.extend([first_block, second_block])
        else:
            adjusted_blocks.append((color, (start, end)))

    img = create_graph(adjusted_blocks)

    return render_template('index.html', img_data=img)


def create_graph(blocks):
    rect_height = 5

    fig, ax = plt.subplots()
    ax.fill_between([0, 24], 0, rect_height, color='grey')

    for color, (start, end) in blocks:
        ax.fill_between([start, end if end != 24 else 24], 0, rect_height, color=color)

    ax.set_xlabel('')
    ax.set_ylim(0, 10)
    ax.tick_params(axis='y', colors='white')
    ax.set_xticks(np.arange(0, 25, 2))

    red_patch = plt.Line2D([], [], color='#d7285c', label='Wake up later')
    yellow_patch = plt.Line2D([], [], color='#e5de1a', label='Wake up sooner')
    green_patch = plt.Line2D([], [], color='#44c53a', label='Maintain schedule')
    grey_patch = plt.Line2D([], [], color='grey', label='Dead zone')
    ax.legend(handles=[red_patch, yellow_patch, green_patch, grey_patch], loc='upper right')

    ax.grid(True)

    figfile = io.BytesIO()
    plt.savefig(figfile, format='png')

    img_data = base64.b64encode(figfile.getvalue()).decode('utf8')
    return img_data


if __name__ == '__main__':
    app.run(debug=True)