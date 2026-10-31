import json, torch
from common import encode, TAB, NL, TAB_ID

def load(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def to_ids(row):
    return encode(row['input'] + TAB + row['output'] + NL)

def pack(rows, block):
    X, Y = [], []
    for row in rows:
        ids = to_ids(row)
        x, y = ids[:-1], ids[1:]
        t = ids.index(TAB_ID)
        y = [-100 if i < t else tok for i, tok in enumerate(y)]
        pad = block - len(x)
        X.append(x + [0] * pad)
        Y.append(y + [-100] * pad)
    return torch.tensor(X), torch.tensor(Y)

if __name__ == '__main__':
    train, val = load('data/train.jsonl'), load('data/val.jsonl')
    block = max(len(to_ids(r)) for r in train + val) + 8
    torch.save(pack(train, block), 'data/train.pt')
    torch.save(pack(val, block), 'data/val.pt')
    with open('data/meta.json', 'w') as f:
        json.dump({'block_size': block}, f)
    print('block_size', block, '| train', len(train), '| val', len(val))
