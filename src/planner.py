import json, torch
from common import VOCAB_SIZE, CFG, NL_ID, encode, decode
from model import SmallLM

def load_model(path='checkpoints/model.pt'):
    block = json.load(open('data/meta.json'))['block_size']
    model = SmallLM(VOCAB_SIZE, block, **CFG)
    model.load_state_dict(torch.load(path, map_location='cpu'))
    return model.eval(), block

@torch.no_grad()
def text_to_plan(model, text, block):
    ids = encode(' '.join(text.lower().split()) + chr(9))
    out = []
    for _ in range(block - len(ids)):
        idx = torch.tensor([ids + out])
        nxt = model(idx)[0][0, -1].argmax().item()   # greedy: same input, same output
        if nxt == NL_ID:
            return decode(out)
        if nxt == 0:
            break
        out.append(nxt)
    return ''   # no clean ending -> treated as 'not understood'
