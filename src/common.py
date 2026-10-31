#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import re

TAB, NL = chr(9), chr(10)
CHARS = ''.join(chr(i) for i in range(32, 127)) + TAB + NL
STOI = {c: i + 1 for i, c in enumerate(CHARS)}   # id 0 = padding
ITOS = {i: c for c, i in STOI.items()}
VOCAB_SIZE = len(CHARS) + 1
TAB_ID, NL_ID = STOI[TAB], STOI[NL]
CFG = {'n_layers': 4, 'n_heads': 4, 'd_model': 128}

def encode(text):
    return [STOI[c] for c in text if c in STOI]

def decode(ids):
    return ''.join(ITOS.get(i, '') for i in ids)

PART_RE = re.compile(r'^(MOVE [FB] [0-9]+([.][0-9]+)?|TURN [LR] [0-9]+([.][0-9]+)?(deg|s))$')

def parse_plan(text):
    
    steps = []
    for part in text.split(';'):
        part = part.strip()
        if not PART_RE.match(part):
            return None
        w = part.split()
        if w[0] == 'MOVE':
            steps.append({'kind': 'move', 'dir': w[1], 'dist': float(w[2])})
        elif w[2].endswith('deg'):
            steps.append({'kind': 'turn', 'dir': w[1], 'angle': float(w[2][:-3])})
        else:
            steps.append({'kind': 'turn', 'dir': w[1], 'secs': float(w[2][:-1])})
    return steps

def within_limits(steps):
    for s in steps:
        key = [k for k in ('dist', 'angle', 'secs') if k in s][0]
        cap = {'dist': 20, 'angle': 720, 'secs': 60}[key]
        if not 0 < s[key] <= cap:
            return False
    return True
