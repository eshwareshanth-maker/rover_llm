#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import math, re
from common import parse_plan, within_limits
from planner import load_model, text_to_plan
from rover import ODOM_CMD, describe, show_commands, yaw_from_quat, wrap

ODOM_HELP = 'Run in another terminal:  ' + ODOM_CMD + '   (shows /odom)'
NUM = re.compile(r'-?[0-9]+(?:[.][0-9]+)?(?:[eE][-+]?[0-9]+)?')

def ask_pose(message):
    print(message)
    print('Paste 4 numbers from /odom:  x  y  qz  qw   (example: 0.0 0.0 0.0 1.0)')
    while True:
        nums = NUM.findall(input('odom> '))
        if len(nums) != 4:
            print('I need exactly 4 numbers: x y qz qw')
            continue
        x, y, qz, qw = map(float, nums)
        if abs(qz * qz + qw * qw - 1) > 0.05:
            print('qz^2 + qw^2 should be about 1 on flat ground. Check the values.')
            continue
        return {'x': x, 'y': y, 'yaw': yaw_from_quat(qz, qw)}

def start_pose(state):
    p = state['pose']
    if p is not None:
        msg = 'Start from last known pose x=%.2f y=%.2f yaw=%.1f deg? [Y/n] ' % (
            p['x'], p['y'], math.degrees(p['yaw']))
        if input(msg).strip().lower() != 'n':
            return p
    return ask_pose(ODOM_HELP)

def main():
    model, block = load_model()
    state = {'pose': None, 'last': None}   
    print('Rover command assistant. Try: go straight 4 m then 6 m left')
    print('Other inputs: repeat | pose | quit')
    while True:
        text = input('>> ').strip().lower()
        if text in ('quit', 'exit'):
            break
        if text == 'pose':
            print(state['pose'] or 'No pose yet.')
            continue
        if text in ('repeat', 'again'):
            steps = state['last']
            if steps is None:
                print('Nothing to repeat yet.')
                continue
        else:
            steps = parse_plan(text_to_plan(model, text, block))
            if steps is None or not within_limits(steps):
                print('I could not turn that into a safe plan. Try: go forward 3 m then turn left 90 degrees')
                continue
        print('I understood:')
        for i, s in enumerate(steps, 1):
            print(f'  {i}. {describe(s)}')
        if input('Correct? [y/n] ').strip().lower() != 'y':
            continue
        end = show_commands(steps, start_pose(state))
        state['last'] = steps
        print()
        ans = input('When the rover has stopped press Enter to enter the final odom (or type skip): ')
        if ans.strip().lower() == 'skip':
            state['pose'] = end
            continue
        actual = ask_pose(ODOM_HELP)
        dx, dy = actual['x'] - end['x'], actual['y'] - end['y']
        dyaw = math.degrees(wrap(actual['yaw'] - end['yaw']))
        print(f'Error vs expected: dx={dx:+.3f} m  dy={dy:+.3f} m  dyaw={dyaw:+.1f} deg')
        state['pose'] = actual

if __name__ == '__main__':
    main()
