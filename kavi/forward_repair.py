"""Continue from the latest circuit, optionally adding one learned jump.

No predecessor participates in inference, and no update restores its parameters.
Earlier verified responses are external teaching/evaluation data, not a lookup
table inside the network. All measured parameters remain trainable.
"""

import copy
from dataclasses import asdict

import torch
from torch import nn

from .file_io import atomic_replace
from .flow_preservation import _backward
from .repair_trials import RepairLearner, RepairNetwork
from .wave_core import WaveConfig


class ForwardNetwork(RepairNetwork):
    def __init__(self, config, slots):
        if not 1 <= slots <= 16:
            raise ValueError("Forward repair is bounded to 16 total repair slots.")
        super().__init__(config, min(slots, 8, config.nodes))
        added = slots - self.repair_slots
        if added:
            for name in ("repair_context", "repair_bias", "repair_gain", "repair_phase"):
                old = getattr(self, name)
                zeros = old.new_zeros((added,) + old.shape[1:])
                setattr(self, name, nn.Parameter(torch.cat((old, zeros), dim=0)))
            for name in ("repair_sources", "repair_destinations"):
                old = getattr(self, name)
                setattr(self, name, torch.cat((old, old.new_zeros(added))))
        self.repair_slots = slots


class ForwardLearner(RepairLearner):
    @classmethod
    def from_latest(cls, latest, jumps=()):
        """Copy the full latest configuration and its optimizer, then extend."""
        n, old_slots = latest.config.nodes, latest.network.repair_slots
        jumps = tuple(tuple(pair) for pair in jumps)
        if len(set(jumps)) != len(jumps) or any(
                len(pair) != 2 or any(not isinstance(v, int) or not 0 <= v < n for v in pair)
                for pair in jumps):
            raise ValueError("Jumps must be distinct, in-range (source, destination) pairs.")
        child = cls(latest.config)
        with torch.random.fork_rng():
            torch.manual_seed(latest.config.seed + 911)
            child.network = ForwardNetwork(latest.config, old_slots + len(jumps))
        child.mode = "adapter_joint"
        child.configure_trainable()
        before = dict(latest.network.named_parameters())
        with torch.no_grad():
            for name, parameter in child.network.named_parameters():
                old = before[name]
                if parameter.shape == old.shape:
                    parameter.copy_(old)
                elif name.startswith("repair_") and parameter.shape[1:] == old.shape[1:]:
                    parameter[:old_slots].copy_(old)
                    parameter[old_slots:].zero_()
                else:
                    raise ValueError("Only repair rows may expand.")
            for name, buffer in child.network.named_buffers():
                old = dict(latest.network.named_buffers())[name]
                if buffer.shape == old.shape:
                    buffer.copy_(old)
                elif name in ("repair_sources", "repair_destinations"):
                    buffer[:old_slots].copy_(old)
            for offset, (source, destination) in enumerate(jumps, old_slots):
                child.network.repair_sources[offset] = source
                child.network.repair_destinations[offset] = destination
        child.optimizer = torch.optim.Adam(child.network.parameters(), lr=latest.config.learning_rate)
        # Preserve original moments and scalar step counters; new rows start at zero.
        for name, parameter in child.network.named_parameters():
            old = before[name]
            for key, value in latest.optimizer.state.get(old, {}).items():
                if isinstance(value, torch.Tensor) and value.shape == old.shape and old.shape != parameter.shape:
                    expanded = torch.zeros_like(parameter)
                    expanded[:old_slots] = value
                    child.optimizer.state[parameter][key] = expanded
                else:
                    child.optimizer.state[parameter][key] = value.clone() if isinstance(value, torch.Tensor) else copy.deepcopy(value)
        child.updates, child.bytes_seen = latest.updates, latest.bytes_seen
        child.parallel_rows = latest.parallel_rows
        return child

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        torch.save({"schema": "forward-repair-1", "slots": self.network.repair_slots,
                    "config": asdict(self.config), "network": self.network.state_dict(),
                    "optimizer": self.optimizer.state_dict(),
                    "updates": self.updates, "bytes_seen": self.bytes_seen}, temporary)
        atomic_replace(temporary, path)

    @classmethod
    def load(cls, path):
        raw = torch.load(path, map_location="cpu", weights_only=True)
        if raw["schema"] != "forward-repair-1":
            raise ValueError("Not a forward-repair checkpoint.")
        child = cls(WaveConfig(**raw["config"]))
        child.network = ForwardNetwork(child.config, raw["slots"])
        child.mode = "adapter_joint"
        child.configure_trainable()
        child.optimizer = torch.optim.Adam(child.network.parameters(), lr=child.config.learning_rate)
        child.network.load_state_dict(raw["network"])
        child.optimizer.load_state_dict(raw["optimizer"])
        child.updates, child.bytes_seen = raw["updates"], raw["bytes_seen"]
        return child


def jump_pool(core):
    """Eight bounded endpoint candidates, never a global shortest-path search."""
    n = core.config.nodes
    occupied = {(int(s), d) for d, row in enumerate(core.network.sources) for s in row}
    occupied |= set(zip(core.network.repair_sources.tolist(), core.network.repair_destinations.tolist()))
    candidates = []
    for i in range(8):
        destination = i * n // 8
        for advance in range(n):
            source = (destination + n // 2 + i + advance) % n
            pair = (source, destination)
            if source != destination and pair not in occupied and pair not in candidates:
                candidates.append(pair)
                break
    if not candidates:
        raise ValueError("No unoccupied jump in the bounded grammar.")
    return candidates


def choose_jump(latest, focus, reference):
    """Select a zero-effect new edge using feedback gradients, without learning."""
    candidates = jump_pool(latest)
    probe = ForwardLearner.from_latest(latest, candidates)
    probe.optimizer.zero_grad(set_to_none=True)
    _backward(probe, focus, 0.5)
    _backward(probe, reference, 0.5)
    gradients = probe.network.repair_gain.grad[latest.network.repair_slots:].detach()
    if not torch.isfinite(gradients).all():
        raise ArithmeticError("Non-finite jump-selection gradient.")
    chosen = int(gradients.abs().argmax())
    return candidates[chosen], {
        "candidates": candidates, "gain_gradients": gradients.tolist(),
        "chosen_index": chosen, "probe_presentations": 8,
        "rule": "Largest absolute initial gain gradient among equal-cost candidate jumps.",
        "probe_ledger": probe.ledger(),
    }


def correct_keys(scores):
    return {q["key"] for group in scores.values() for q in group["outputs"] if q["correct"]}


def preservation(old_scores, latest_scores, current_scores):
    old, latest, current = map(correct_keys, (old_scores, latest_scores, current_scores))
    return {"old_correct": len(old), "latest_correct": len(latest),
            "union_correct": len(old | latest), "current_correct": len(current),
            "old_lost": len(old-current), "latest_lost": len(latest-current),
            "union_lost": len((old | latest)-current),
            "old_regressions_repaired": len((old-latest) & current),
            "outside_union_gained": len(current-(old | latest))}


def feedback_batch(rng, questions, old_keys, latest_keys, current_keys):
    """Teach mistakes while rehearsing successes of BOTH configurations."""
    by_key = {q.key: q for q in questions}
    all_keys = set(by_key)

    def pick(preferred, fallback, count=2):
        pool = sorted(preferred or fallback or all_keys)
        return [by_key[rng.choice(pool)] for _ in range(count)]

    wrong = all_keys-current_keys
    focus = pick(old_keys-current_keys, wrong) + pick(latest_keys-current_keys, wrong)
    reference = pick(old_keys, all_keys) + pick(latest_keys, all_keys)
    return focus, reference
