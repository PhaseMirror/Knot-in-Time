# Architecture: Functorial Zeno Sheaf with Memory Kernel (FZS-MK)
# Purpose: Replaces standard self-attention with a projective attention rule

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class ZetaAttention(nn.Module):
    """
    Implements the Log-Periodic Zeta-Attention mechanism.
    Enforces the Constitutional Vocabulary Charter via a hard Boolean mask.
    """

    def __init__(self, d_model, n_heads, vocab_size, n_zeros=10, kappa=1.0):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        self.vocab_size = vocab_size
        self.kappa = kappa

        # Precompute imaginary parts of the Riemann zeta zeros (gamma_n)
        # These inject the non-Markovian Zeno timing structure into the network
        self.register_buffer(
            "gamma",
            torch.tensor(
                [
                    14.1347,
                    21.0220,
                    25.0109,
                    30.4249,
                    32.9351,
                    37.5862,
                    40.9187,
                    43.3271,
                    48.0052,
                    49.7738,
                ][:n_zeros]
            ),
        )

        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)

        # Initialize the Boolean Cohomology Mask (Omega) from the Vocabulary Charter
        # 1 = Topologically valid, 0 = Unphysical degree of freedom (Adversarial)
        self.register_buffer("omega_mask", torch.ones(vocab_size, vocab_size))

    def load_constitutional_mask(self, charter_matrix):
        """Loads the validated boolean mask derived from vocabulary_charter.yaml"""
        self.omega_mask.copy_(charter_matrix)

    def _memory_kernel(self, i, j):
        """
        Log-Periodic Memory Kernel K(i,j) derived from Riemann zeros.
        Prevents slow adversarial drift through repeated context.
        """
        delta = torch.abs(i - j)
        decay = torch.exp(-self.kappa * delta)

        log_delta = torch.log(delta + 1.0)
        cos_sum = torch.zeros_like(delta)
        for g in self.gamma:
            cos_sum += torch.cos(g * log_delta)

        return decay * cos_sum

    def forward(self, x, semantic_token_ids, causal_mask=None):
        # x: (batch, seq_len, d_model)
        # semantic_token_ids: (batch, seq_len) - The actual vocabulary IDs
        batch, seq_len, _ = x.shape

        Q = self.w_q(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = self.w_k(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        V = self.w_v(x).view(batch, seq_len, self.n_heads, self.d_k).transpose(1, 2)

        # Standard scaled dot-product
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # Apply Log-Periodic Memory Kernel (mathcal{K})
        i_idx = torch.arange(seq_len, device=x.device).float().unsqueeze(1)
        j_idx = torch.arange(seq_len, device=x.device).float().unsqueeze(0)
        M = self._memory_kernel(i_idx, j_idx).unsqueeze(0).unsqueeze(0)

        # Modulate logits by the memory kernel
        scores = scores * M

        # Map actual semantic token IDs to their specific Boolean Cohomology (Omega)
        # Shape: (batch, seq_len, seq_len) -> Broadcast to heads
        seq_omega = self.omega_mask[
            semantic_token_ids.unsqueeze(2), semantic_token_ids.unsqueeze(1)
        ]
        seq_omega = seq_omega.unsqueeze(1)

        # APPLY THE HARD BOOLEAN MASK (The Ward Identity)
        # If Omega = 0, the interaction violates constitutional geometry and is penalized with -1e9.
        scores = scores.masked_fill(seq_omega == 0, -1e9)

        if causal_mask is not None:
            scores = scores.masked_fill(causal_mask == 0, -1e9)

        attn = F.softmax(scores, dim=-1)

        out = torch.matmul(attn, V)
        out = out.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        return self.w_o(out)
