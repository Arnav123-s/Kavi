"""Experimental plasticity and bounded topology changes, never live rollout.

The growth rule duplicates one incoming route per node before perturbing it.
Without perturbation, subtracting log(2) from both duplicate logits preserves
the original softmax-normalized message in exact arithmetic. Rewiring is not
function preserving. Both changes are tested, not assumed beneficial.
"""

from dataclasses import replace
import math

import torch
from torch import nn
from torch.nn import functional as F

from .wave_core import WaveLearner


VARIANTS = ("standard", "damped_routes", "rewire", "split_growth")
ROUTE_NAMES = ("edge_logits", "phase", "conductance", "activity_gain")


class TrialLearner(WaveLearner):
    """Same byte objective, optional serial microbatches, one optimizer step."""

    def __init__(self, config):
        super().__init__(config)
        self.variant = "standard"
        self.parallel_rows = 4
        self.adaptations = []

    def learn_answers(self, examples, callback=None):
        if self.variant not in VARIANTS or not 1 <= len(examples) <= 4 or self.parallel_rows not in (1, 2, 4):
            raise ValueError("Invalid experimental learning budget.")
        anchors = {name: getattr(self.network, name).detach().clone() for name in ROUTE_NAMES} if self.variant == "damped_routes" else {}
        self.network.train()
        self.optimizer.zero_grad(set_to_none=True)
        loss_value, tokens = 0.0, 0
        for start in range(0, len(examples), self.parallel_rows):
            chunk = examples[start:start+self.parallel_rows]
            encoded = []
            for prefix, answer in chunk:
                p, a = prefix.encode(), (answer + "\n").encode()
                if not p or not answer or len(p + a) > 256:
                    raise ValueError("Invalid answer-training example.")
                encoded.append((p, a))
            length = max(len(p) + len(a) - 1 for p, a in encoded)
            x = torch.zeros(len(encoded), length, dtype=torch.long)
            target = torch.full_like(x, -100)
            for row, (p, a) in enumerate(encoded):
                values = torch.tensor(list(p + a), dtype=torch.long)
                x[row, :len(values)-1] = values[:-1]
                target[row, len(p)-1:len(values)-1] = values[len(p):]
            logits, _ = self.network(x)
            losses = F.cross_entropy(logits.transpose(1, 2), target, ignore_index=-100, reduction="none")
            mask = target != -100
            loss = (losses.sum(1) / mask.sum(1)).sum() / len(examples)
            if not torch.isfinite(loss):
                raise ArithmeticError("Non-finite experimental answer loss.")
            loss.backward()
            loss_value += float(loss.detach())
            tokens += int(mask.sum())
        norm = nn.utils.clip_grad_norm_(self.network.parameters(), 1.0, error_if_nonfinite=True)
        self.optimizer.step()
        if anchors:
            with torch.no_grad():
                for name, old in anchors.items():
                    value = getattr(self.network, name)
                    value.copy_(old + 0.25 * (value - old))
        self.updates += 1
        self.bytes_seen += tokens
        event = {"loss": loss_value, "tokens": tokens, "update": self.updates,
                 "gradient_norm": float(norm), "parallel_rows": self.parallel_rows,
                 "variant": self.variant, "objective": "balanced-answer-only"}
        event["interrupted"] = callback(event) is False if callback else False
        return event

    def rewire_weak_routes(self):
        """One changed incoming source per node; no parameter growth."""
        if self.adaptations:
            raise ValueError("Only one topology change is allowed per trial.")
        net, n = self.network, self.config.nodes
        with torch.no_grad():
            weak = (net.edge_logits.softmax(-1) * net.conductance.sigmoid()).argmin(-1)
            for destination in range(n):
                occupied = set(net.sources[destination].tolist())
                source = next((destination + offset) % n for offset in range(1, n)
                              if (destination + offset) % n not in occupied)
                slot = int(weak[destination])
                net.sources[destination, slot] = source
                # Retain the low-strength route's parameters, reset its moments.
                for name in ROUTE_NAMES:
                    parameter = getattr(net, name)
                    for value in self.optimizer.state[parameter].values():
                        if isinstance(value, torch.Tensor) and value.shape == parameter.shape:
                            value[destination, slot] = 0
        self.adaptations.append({"kind": "rewire", "changed_sources": n,
                                 "available_links": n * self.config.fan_in})

    def grow_split_routes(self, perturbation=0.015):
        """At most one extra incoming route per node; migrate optimizer state."""
        if self.adaptations or self.config.fan_in >= 5 or self.config.nodes > 64:
            raise ValueError("Growth is capped at one expansion, 64 nodes and fan-in five.")
        old, old_optimizer = self.network, self.optimizer
        n, k = self.config.nodes, self.config.fan_in
        config = replace(self.config, fan_in=k+1)
        expanded = WaveLearner(config)
        weak = (old.edge_logits.softmax(-1) * old.conductance.sigmoid()).argmin(-1)
        row = torch.arange(n)
        with torch.no_grad():
            for name, new_parameter in expanded.network.named_parameters():
                original = dict(old.named_parameters())[name]
                if name in ROUTE_NAMES:
                    new_parameter[:, :k].copy_(original)
                    new_parameter[:, k].copy_(original[row, weak])
                else:
                    new_parameter.copy_(original)
            expanded.network.sources[:, :k].copy_(old.sources)
            expanded.network.sources[:, k].copy_(old.sources[row, weak])
            expanded.network.edge_logits[row, weak] -= math.log(2)
            expanded.network.edge_logits[:, k] -= math.log(2)
            # Explicit symmetry breaking; after this the map is only approximate.
            expanded.network.phase[:, k] += perturbation * torch.where(row % 2 == 0, 1.0, -1.0)
        old_parameters = dict(old.named_parameters())
        for name, parameter in expanded.network.named_parameters():
            original = old_parameters[name]
            for key, value in old_optimizer.state[original].items():
                if isinstance(value, torch.Tensor) and value.shape == original.shape and parameter.shape != original.shape:
                    migrated = torch.zeros_like(parameter)
                    migrated[:, :k] = value
                    expanded.optimizer.state[parameter][key] = migrated
                else:
                    expanded.optimizer.state[parameter][key] = value.clone() if isinstance(value, torch.Tensor) else value
        self.network, self.optimizer, self.config = expanded.network, expanded.optimizer, config
        self.adaptations.append({"kind": "split_growth", "added_available_links": n,
                                 "available_links": n * (k+1), "phase_perturbation": perturbation,
                                 "note": "Duplicated sources, not new destinations; new slots can learn distinct phase/gating behavior."})

    def apply_scheduled_change(self):
        if self.variant == "rewire":
            self.rewire_weak_routes()
        elif self.variant == "split_growth":
            self.grow_split_routes()
