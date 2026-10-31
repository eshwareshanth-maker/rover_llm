#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import json, random

SIDES = {'L': ['left', 'anticlockwise', 'counterclockwise', 'counter clockwise', 'ccw'],
         'R': ['right', 'clockwise', 'cw']}
FWD = ['go', 'move', 'drive', 'travel', 'run', 'go straight', 'move straight', 'drive straight',
       'go forward', 'move forward', 'drive forward']
BACK = ['go back', 'move back', 'go backward', 'move backward', 'drive backward', 'reverse', 'back up']
UNITS = ['m', ' m', ' meter', ' meters', ' metre', ' metres']
TURN_VERBS = ['turn', 'rotate', 'spin', 'pivot']
SECS = ['s', ' s', ' sec', ' seconds', ' second']
ANGLES = [15, 30, 45, 60, 90, 120, 135, 180, 270, 360]
JOINS = [' then ', ', then ', ' and then ', ', ', ' after that ', ' next ']
PREFIX = ['', '', 'please ', 'rover ', 'can you ', 'now ', 'ok ']

def fmt(x):
    return str(int(x)) if x == int(x) else str(x)

def dist():
    return fmt(random.choice([random.randint(1, 10), random.randint(1, 20) / 2]))

def move_step():
    n, fwd = dist(), random.random() < 0.75
    verb = random.choice(FWD if fwd else BACK)
    link = random.choice([' ', ' for ', ' by '])
    d = 'F' if fwd else 'B'
    return verb + link + n + random.choice(UNITS), ['MOVE ' + d + ' ' + n]

def side_step():   
    s, n = random.choice('LR'), dist()
    word = 'left' if s == 'L' else 'right'
    text = n + random.choice(UNITS) + ' ' + random.choice(['', 'to the ']) + word
    return text, ['TURN ' + s + ' 90deg', 'MOVE F ' + n]

def turn_step():
    s = random.choice('LR')
    w, verb, r = random.choice(SIDES[s]), random.choice(TURN_VERBS), random.random()
    if r < 0.35:   # time based
        n = random.randint(1, 20)
        text = verb + ' ' + w + random.choice([' for ', ' ']) + str(n) + random.choice(SECS)
        return text, ['TURN ' + s + ' ' + str(n) + 's']
    if r < 0.8:    # angle based
        a = random.choice([random.choice(ANGLES), random.randint(5, 359)])
        forms = [f'{verb} {w} {a} degrees', f'{verb} {w} by {a} deg',
                 f'{verb} {a} degrees {w}', f'{verb} {w} {a} deg']
        return random.choice(forms), [f'TURN {s} {a}deg']
    if r < 0.92:   # no amount given -> 90 degrees
        return verb + ' ' + w, ['TURN ' + s + ' 90deg']
    return random.choice(['make a u-turn', 'u-turn', 'turn around']), ['TURN L 180deg']

def sample():
    texts, plans = [], []
    for _ in range(random.randint(1, 4)):
        r = random.random()
        step = move_step() if r < 0.4 else turn_step() if r < 0.8 else side_step()
        texts.append(step[0])
        plans += step[1]
    text = random.choice(PREFIX) + random.choice(JOINS).join(texts)
    if random.random() < 0.1:
        text += '.'
    return {'input': text, 'output': '; '.join(plans)}

def build(n, seed, exclude=frozenset()):
    random.seed(seed)
    seen, rows = set(exclude), []
    while len(rows) < n:
        row = sample()
        if row['input'] not in seen:
            seen.add(row['input'])
            rows.append(row)
    return rows

def save(rows, path):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + chr(10))

if __name__ == '__main__':
    train = build(15000, seed=1)
    val = build(500, seed=2, exclude={r['input'] for r in train})
    save(train, 'data/train.jsonl')
    save(val, 'data/val.jsonl')
    for r in train[:3]:
        print(r)
