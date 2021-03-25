import os
from threading import Thread
from sh import tail
from pymouse import PyMouse
from datetime import datetime, timedelta
import subprocess


WAS_MOVED_SCATTER = 1

# in seconds
SHORT_PRESS = .15
MEDIUM_PRESS = .4
LONG_PRESS = .6
VERY_LONG_PRESS = 1

SCROLL_SENSITIVITY = 10
MOVE_SENSITIVITY = .8
MOVE_SCALING = 1.4

def get_time_delta_in_microseconds(t1, t2):
    if t1 == None or t2 == None:
        return 666
    t_d = t2 - t1
    return t_d.seconds + t_d.microseconds / 10 ** 6

m = PyMouse()


cur_start_pos = list(m.position())
cur_anchor_x = None
cur_anchor_y = None
pre_x = None
pre_y = None

def wasnt_moved():
    if cur_anchor_y == None and cur_anchor_x == None:
        return True
    
    return False

    c_p = m.position()
    print(cur_start_pos)
    print(c_p)
    d_x = abs(cur_start_pos[0] - c_p[0]) 
    d_y = abs(cur_start_pos[1] - c_p[1])
    return d_x < WAS_MOVED_SCATTER and d_y < WAS_MOVED_SCATTER


scroll_counter = 0
def scroll(val):
    global scroll_counter
    scroll_counter += val
    if scroll_counter > SCROLL_SENSITIVITY:
        while scroll_counter > SCROLL_SENSITIVITY:
            scroll_counter -= SCROLL_SENSITIVITY
            m.click((4))
    elif scroll_counter < -SCROLL_SENSITIVITY:
        while scroll_counter < -SCROLL_SENSITIVITY:
            scroll_counter += SCROLL_SENSITIVITY
            m.click((5))


# Thread(target = os.system, args = (adb_cmd, )).start()

horizontal = False
press_down_time = None
count_click = 0
count_hold = 0
is_holded = False
is_scrolled = False

is_stop = False

adb_cmd = 'adb shell getevent -l'.split()
# adb_cmd = 'adb shell getevent -l  > event.log'

def sing(val):
    return -1 if val < 0 else 1

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

# Example
# for path in execute(["locate", "a"]):
#     print(path, end="")


# runs forever
# for line in tail("-f", "event.log", _iter=True):
for line in execute(adb_cmd):

    if not is_stop and (
       'ABS_MT_POSITION_X' in line and horizontal or
       'ABS_MT_POSITION_Y' in line and not horizontal):

        unpress_time = get_time_delta_in_microseconds(
            press_down_time, datetime.now()
        )
        if unpress_time > SHORT_PRESS:
            count_click = 0
       
        if (count_click == 1 and wasnt_moved() and not is_holded):
            is_holded = True
            m.press()
            
        val = int(line.split()[3], 16)
        if (pre_x != None):
            d_x = val - pre_x
            pre_x = val
        else:
            pre_x = val
            if not is_scrolled:
                continue

        if not cur_anchor_x:
            cur_anchor_x = val
        elif not is_scrolled:
            d_x = pow(abs(d_x) * MOVE_SENSITIVITY, MOVE_SCALING) * sing(d_x)
            m.move_dx(round(d_x))

    elif not is_stop and (
         'ABS_MT_POSITION_Y' in line and horizontal or
         'ABS_MT_POSITION_X' in line and not horizontal):

        unpress_time = get_time_delta_in_microseconds(
            press_down_time, datetime.now()
        )
        if unpress_time > SHORT_PRESS:
            count_click = 0

        if (count_click == 1 and wasnt_moved() and not is_holded):
            is_holded = True
            m.press()

        val = int(line.split()[3], 16)
        if (pre_y != None):
            d_y = val - pre_y
            pre_y = val
        else:
            pre_y = val
            continue

        if not cur_anchor_y:
            cur_anchor_y = val
        elif is_scrolled:
            scroll(d_y)
        else:
            rev = -1 if not horizontal else 1
            d_y = pow(abs(d_y) * MOVE_SENSITIVITY, MOVE_SCALING) * sing(d_y) * rev
            m.move_dy(round(d_y))
        pre_y = val

    elif 'BTN_TOUCH' in line:
        cur_start_pos = list(m.position())

        val = line.split()[3]
        if val == 'UP':
            if wasnt_moved() and not is_scrolled:
                press_time = get_time_delta_in_microseconds(
                    press_down_time, datetime.now()
                )
                if press_time < SHORT_PRESS:
                    count_click += 1
                elif not is_stop and press_time < MEDIUM_PRESS:
                    m.click(2)
                else:
                    count_click = 0

                if not is_stop and count_click == 1:
                    m.click()
                if not is_stop and count_click == 2:
                    m.click()
                elif count_click == 5:
                    is_stop = not is_stop
            else:
                count_click = 0
            
            if is_holded:
                is_holded = False
                m.release()

            is_scrolled = False

            press_down_time = datetime.now()
        else:
            unpress_time = get_time_delta_in_microseconds(
                press_down_time, datetime.now()
            )
            if unpress_time > SHORT_PRESS:
                count_click = 0

            if not horizontal and pre_x > 1600:
                is_scrolled = True

            press_down_time = datetime.now()
            # count_hold += 1
            # m.press()

        cur_anchor_x = None
        cur_anchor_y = None

    elif 'ABS_MT_PRESSURE' in line:
        pass
        # print(line, end = '')

    # print(line)
