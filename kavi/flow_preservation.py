"""First-order retention constraint on a changing circuit, without freezing.

This projects Adam's displacement, not the raw gradient used by A-GEM. It
protects the linearized average loss on sampled rehearsal, not every answer.
"""

import torch
from torch import nn
from torch.nn import functional as F


def project_displacement(displacements, reference_gradients):
    dot = sum((d * g).sum() for d, g in zip(displacements, reference_gradients))
    norm2 = sum(g.square().sum() for g in reference_gradients)
    if not torch.isfinite(dot) or not torch.isfinite(norm2):
        raise ArithmeticError("Non-finite preservation projection.")
    projected = float(dot) > 0 and float(norm2) > 1e-20
    scale = dot / norm2 if projected else torch.zeros_like(dot)
    corrected = [d - scale * g for d, g in zip(displacements, reference_gradients)]
    after = sum((d * g).sum() for d, g in zip(corrected, reference_gradients))
    return corrected, {"projected": projected, "reference_dot_before": float(dot),
                       "reference_dot_after": float(after)}


def _backward(core, examples, factor):
    if len(examples) != 4:
        raise ValueError("Use four focus and four reference examples.")
    value, count = 0.0, 0
    for start in range(0, 4, core.parallel_rows):
        encoded = []
        for prefix, answer in examples[start:start+core.parallel_rows]:
            p, a = prefix.encode(), (answer + "\n").encode()
            if not p or not answer or len(p+a) > 256:
                raise ValueError("Invalid bounded flow example.")
            encoded.append((p, a))
        length = max(len(p)+len(a)-1 for p, a in encoded)
        x = torch.zeros(len(encoded), length, dtype=torch.long)
        target = torch.full_like(x, -100)
        for row, (p, a) in enumerate(encoded):
            data = torch.tensor(list(p+a), dtype=torch.long)
            x[row, :len(data)-1] = data[:-1]
            target[row, len(p)-1:len(data)-1] = data[len(p):]
        logits, _ = core.network(x)
        losses = F.cross_entropy(logits.transpose(1, 2), target, ignore_index=-100, reduction="none")
        mask = target != -100
        loss = (losses.sum(1) / mask.sum(1)).sum() / 4
        if not torch.isfinite(loss):
            raise ArithmeticError("Non-finite flow-preservation loss.")
        (factor * loss).backward()
        value += float(loss.detach())
        count += int(mask.sum())
    return value, count


def learn_with_rehearsal(core, focus, reference, *, project=False):
    """All arms use the same eight examples and one mean-loss Adam proposal."""
    if core.parallel_rows not in (1, 2, 4):
        raise ValueError("Invalid microbatch width.")
    parameters = [p for p in core.network.parameters() if p.requires_grad]
    core.network.train()
    core.optimizer.zero_grad(set_to_none=True)
    reference_loss, n_reference = _backward(core, reference, 1.0)
    gradients = [p.grad.detach().clone() if p.grad is not None else torch.zeros_like(p) for p in parameters]
    for p in parameters:
        if p.grad is not None:
            p.grad.mul_(0.5)
    focus_loss, n_focus = _backward(core, focus, 0.5)
    norm = nn.utils.clip_grad_norm_(parameters, 1.0, error_if_nonfinite=True)
    original = [p.detach().clone() for p in parameters] if project else []
    core.optimizer.step()
    event = {"projected": False}
    if project:
        with torch.no_grad():
            displacement = [p - old for p, old in zip(parameters, original)]
            corrected, event = project_displacement(displacement, gradients)
            for p, old, delta in zip(parameters, original, corrected):
                p.copy_(old + delta)
    core.updates += 1
    core.bytes_seen += n_focus+n_reference
    return {**event, "loss": (focus_loss+reference_loss)/2, "focus_loss": focus_loss,
            "reference_loss": reference_loss, "gradient_norm": float(norm),
            "tokens": n_focus+n_reference, "update": core.updates,
            "objective": "equal-focus-and-reference-answer-loss", "presentations": 8}
