#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import json
from planner import load_model, text_to_plan

def evaluate(n=200):
    model, block = load_model()
    with open('data/val.jsonl', encoding='utf-8') as f:
        rows = [json.loads(line) for line in f][:n]
    bad = []
    for r in rows:
        got = text_to_plan(model, r['input'], block)
        if got != r['output']:
            bad.append((r['input'], r['output'], got))
    print(f'exact match: {len(rows) - len(bad)}/{len(rows)}')
    for b in bad[:10]:
        print('IN  :', b[0])
        print('WANT:', b[1])
        print('GOT :', b[2])
        print()

if __name__ == '__main__':
    evaluate()
