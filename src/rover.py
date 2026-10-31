import math

LIN_SPEED = 0.2      # m/s   - edit to match your rover
ANG_SPEED = 0.5      # rad/s - edit to match your rover
RATE_HZ = 10
ODOM_CMD = 'python3 odom.py'
RELAY_CMD = 'python3 cmd_vel_relay.py'
Q = chr(34)

def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))

def yaw_from_quat(qz, qw):
    return math.atan2(2 * qw * qz, 1 - 2 * qz * qz)

def describe(step):
    if step['kind'] == 'move':
        way = 'forward' if step['dir'] == 'F' else 'backward'
        dist = step['dist']
        return f'MOVE {way} {dist:g} m'
    way = 'left / counter-clockwise' if step['dir'] == 'L' else 'right / clockwise'
    if 'angle' in step:
        amount = 'by ' + format(step['angle'], 'g') + ' deg'
    else:
        amount = 'for ' + format(step['secs'], 'g') + ' s'
    return 'TURN ' + way + ' ' + amount

def to_twist(step):
    if step['kind'] == 'move':
        v = LIN_SPEED if step['dir'] == 'F' else -LIN_SPEED
        return {'lin': v, 'ang': 0.0, 'dur': step['dist'] / LIN_SPEED}
    w = ANG_SPEED if step['dir'] == 'L' else -ANG_SPEED   # ROS: +z is counter-clockwise
    dur = step['secs'] if 'secs' in step else math.radians(step['angle']) / ANG_SPEED
    return {'lin': 0.0, 'ang': w, 'dur': dur}

def advance(pose, tw):
    d = tw['lin'] * tw['dur']
    yaw = pose['yaw']
    return {'x': pose['x'] + d * math.cos(yaw), 'y': pose['y'] + d * math.sin(yaw),
            'yaw': wrap(yaw + tw['ang'] * tw['dur'])}

def pub_cmd(lin, ang, dur=None):
    body = (Q + '{linear: {x: ' + f'{lin:.3f}' + ', y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: '
            + f'{ang:.3f}' + '}}' + Q)
    if dur is None:
        return 'ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist ' + body
    return f'timeout {dur:.1f} ros2 topic pub -r {RATE_HZ} /cmd_vel geometry_msgs/msg/Twist ' + body

def show_commands(steps, pose):
    print()
    print('=== COMMANDS TO RUN (Ubuntu / WSL terminals) ===')
    print('Terminal A:  ' + RELAY_CMD)
    print('Terminal B:  run these in order, waiting for each to finish')
    for i, st in enumerate(steps, 1):
        tw = to_twist(st)
        pose = advance(pose, tw)
        lin, ang, dur = tw['lin'], tw['ang'], tw['dur']
        px, py, yaw_deg = pose['x'], pose['y'], math.degrees(pose['yaw'])
        print()
        print(f'Step {i}: {describe(st)}')
        print('  topic: /cmd_vel   type: geometry_msgs/msg/Twist')
        print(f'  linear  x={lin:+.3f} m/s  y=+0.000  z=+0.000')
        print(f'  angular x=+0.000  y=+0.000  z={ang:+.3f} rad/s')
        print(f'  hold for {dur:.2f} s, then publish all zeros')
        print('  ' + pub_cmd(lin, ang, dur))
        print('  ' + pub_cmd(0, 0))
        print(f'  expected /odom afterwards: x={px:.3f} y={py:.3f} yaw={yaw_deg:.1f} deg')
    return pose
