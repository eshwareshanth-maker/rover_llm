#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import json, math, os, time, torch
from common import VOCAB_SIZE, CFG
from model import SmallLM

torch.set_num_threads(os.cpu_count())
torch.manual_seed(0)

def lr_at(step, max_steps, base, warmup=100):
    if step < warmup:
        return base * (step + 1) / warmup
    p = (step - warmup) / max(1, max_steps - warmup)
    return base * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * p)))

def batch(data, bs):
    X, Y = data
    ix = torch.randint(len(X), (bs,))
    return X[ix], Y[ix]

def train(max_steps=3000, bs=32, lr=1e-3, eval_every=200):
    block = json.load(open('data/meta.json'))['block_size']
    train_data, val_data = torch.load('data/train.pt'), torch.load('data/val.pt')
    model = SmallLM(VOCAB_SIZE, block, **CFG)
    n_params = sum(p.numel() for p in model.parameters())
    print(f'params {n_params / 1e6:.2f}M | block {block} | threads {torch.get_num_threads()}')
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    t0 = time.time()
    for step in range(max_steps):
        for g in opt.param_groups:
            g['lr'] = lr_at(step, max_steps, lr)
        x, y = batch(train_data, bs)
        _, loss = model(x, y)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        if step % eval_every == 0 or step == max_steps - 1:
            model.eval()
            with torch.no_grad():
                _, vl = model(*batch(val_data, 100))
            model.train()
            print(f'step {step:5d} | train {loss.item():.4f} | val {vl.item():.4f} | {time.time() - t0:.0f}s')
    torch.save(model.state_dict(), 'checkpoints/model.pt')
    print('saved checkpoints/model.pt')

if __name__ == '__main__':
    train()
