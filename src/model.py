#author: Eshanth Eshwar M
#email: eshwareshanth@gmial.com

import torch
import torch.nn as nn
import torch.nn.functional as F

def block(layer, x, n_heads):
    B, T, C = x.shape
    q, k, v = layer['qkv'](layer['ln1'](x)).split(C, dim=-1)
    q, k, v = (t.view(B, T, n_heads, C // n_heads).transpose(1, 2) for t in (q, k, v))
    a = F.scaled_dot_product_attention(q, k, v, is_causal=True)
    x = x + layer['proj'](a.transpose(1, 2).reshape(B, T, C))
    return x + layer['fc2'](F.gelu(layer['fc1'](layer['ln2'](x))))

class SmallLM(nn.Module):
    def __init__(self, vocab_size, block_size, n_layers=4, n_heads=4, d_model=128):
        super().__init__()
        self.n_heads = n_heads
        self.tok = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Embedding(block_size, d_model)
        self.layers = nn.ModuleList([nn.ModuleDict({
            'ln1': nn.LayerNorm(d_model), 'qkv': nn.Linear(d_model, 3 * d_model),
            'proj': nn.Linear(d_model, d_model), 'ln2': nn.LayerNorm(d_model),
            'fc1': nn.Linear(d_model, 4 * d_model), 'fc2': nn.Linear(4 * d_model, d_model),
        }) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size, bias=False)
        self.head.weight = self.tok.weight   # tie input/output embeddings

    def forward(self, idx, targets=None):
        B, T = idx.shape
        x = self.tok(idx) + self.pos(torch.arange(T, device=idx.device))
        for layer in self.layers:
            x = block(layer, x, self.n_heads)
        logits = self.head(self.ln_f(x))
        if targets is None:
            return logits, None
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1), ignore_index=-100)
        return logits, loss
