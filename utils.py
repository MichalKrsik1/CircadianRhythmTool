import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from constants import RED_COLOR, YELLOW_COLOR, GREEN_COLOR, GREY_COLOR


def calculate_blocks(wake_time_hours):
    tm = wake_time_hours - 2

    red_block = ('#d7285c', ((tm - 4) % 24, tm % 24))
    yellow_block = ('#e5de1a', (tm % 24, wake_time_hours % 24))
    green_block = ('#44c53a', (wake_time_hours % 24, (wake_time_hours + 4) % 24))

    return [red_block, yellow_block, green_block]


def adjust_blocks(blocks):
    adjusted_blocks = []
    for color, (start, end) in blocks:
        if start > end:
            adjusted_blocks.extend([(color, (start, 24)), (color, (0, end))])
        else:
            adjusted_blocks.append((color, (start, end)))
    return adjusted_blocks


def create_sleep_impact_graph(blocks, day_number=None):
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

    if day_number:
        plt.title(f'Day {day_number}')
    else:
        plt.title('How and when light exposure affects your wake up time')

    figfile = io.BytesIO()
    plt.savefig(figfile, format='png')

    img_data = base64.b64encode(figfile.getvalue()).decode('utf8')
    return img_data
