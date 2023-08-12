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
