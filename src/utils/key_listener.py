import time
import keyboard

ignored_keys = {'enter', 'backspace', 'caps lock', 'tab',
                'shift', 'ctrl', 'alt', 'left', 'up', 'down', 'right'}


def collect_data_for_input():
    password = []
    intervals_list = []
    holdings_time_list = []
    last_press_time_dict = {}

    def key_pressed(event):
        nonlocal password

        # Обработка события при нажатии клавиши
        if event.event_type == 'down':
            if event.name == 'backspace' and len(password) > 0 and len(intervals_list) > 0 and len(holdings_time_list):
                password.pop()
                intervals_list.pop()
                holdings_time_list.pop()
            elif event.name not in ignored_keys:
                if password and last_press_time_dict.get(password[-1], None) is not None:
                    intervals_list.append(time.time() - last_press_time_dict.get(password[-1]))
                last_press_time_dict[event.name] = time.time()
                password.append(event.name)

        # Обработка события при отпускании клавиши
        elif event.event_type == 'up':
            if event.name not in ignored_keys:
                holding_time = time.time() - last_press_time_dict[event.name]
                holdings_time_list.append(holding_time)

    keyboard.hook(key_pressed)
    keyboard.wait('enter')
    keyboard.unhook_all()
    password = "".join([char for char in password])

    return password, intervals_list, holdings_time_list
