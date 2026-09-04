"""A small, internally trained, classical complex-valued pathway circuit.

No answer rules, source lookup, or transcript database live in this core.
The teacher presents bytes and corrections. Autograd changes the fixed graph's
input encodings, transmission strengths, phases, gates, and output encodings.
This is a sparse recurrent neural model, not a quantum computer or a proof of
an advantage over ordinary recurrent networks.
"""

from __future__ import annotations

from .file_io import atomic_replace

from dataclasses import asdict, dataclass
import hashlib
import math
from pathlib import Path
from typing import Callable

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class WaveConfig:
    nodes: int = 64
    fan_in: int = 4
    hops: int = 2
    sequence_length: int = 64
    learning_rate: float = 0.003
    seed: int = 4301
    threads: int = 2
    phase_enabled: bool = True

    def __post_init__(self) -> None:
        if not 8 <= self.nodes <= 256 or not 1 <= self.fan_in <= 8:
            raise ValueError("Circuit budget is 8..256 nodes and 1..8 incoming links.")
        if not 1 <= self.hops <= 4 or not 8 <= self.sequence_length <= 256:
            raise ValueError("Hops or sequence length exceeds the bounded budget.")
        if not 1 <= self.threads <= 4 or not 0 < self.learning_rate <= 0.02:
            raise ValueError("Invalid CPU or learning-rate budget.")


class WaveNetwork(nn.Module):
    """Fixed sparse substrate; data-dependent gates and learned phase rotation."""

    def __init__(self, config: WaveConfig) -> None:
        super().__init__()
        self.config = config
        n, k = config.nodes, config.fan_in
        self.embedding = nn.Embedding(256, n * 2)
        self.readout = nn.Linear(n * 2, 256)
        self.edge_logits = nn.Parameter(torch.zeros(n, k))
        self.phase = nn.Parameter(torch.randn(n, k) * 0.15,
                                  requires_grad=config.phase_enabled)
        self.conductance = nn.Parameter(torch.zeros(n, k))
        self.activity_gain = nn.Parameter(torch.zeros(n, k))
        self.memory_gate = nn.Parameter(torch.ones(n) * 0.5)
        offsets = torch.tensor([0, 1, 3, 7, 13, 23, 37, 53][:k])
        self.register_buffer("sources", (torch.arange(n)[:, None] + offsets) % n)
        nn.init.normal_(self.embedding.weight, std=0.08)
        nn.init.normal_(self.readout.weight, std=0.04)
        nn.init.zeros_(self.readout.bias)

    def step(self, token: torch.Tensor, state: torch.Tensor,
             hops: int | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        c = self.config
        incoming = self.embedding(token).reshape(-1, c.nodes, 2)
        gate = torch.sigmoid(self.memory_gate)[None, :, None]
        z = gate * state + (1 - gate) * incoming
        phase = self.phase if c.phase_enabled else self.phase * 0
        co, si = phase.cos(), phase.sin()
        for _ in range(hops or c.hops):
            neighbors = z[:, self.sources, :]
            strength = neighbors.square().sum(-1).sqrt()
            routing = (self.edge_logits + torch.tanh(self.activity_gain) * strength).softmax(-1)
            transmission = routing * torch.sigmoid(self.conductance)
            real, imag = neighbors[..., 0], neighbors[..., 1]
            mr = (transmission * (co * real - si * imag)).sum(-1)
            mi = (transmission * (si * real + co * imag)).sum(-1)
            message = torch.stack((mr, mi), -1)
            z = z + 0.5 * message + 0.25 * incoming
            z = z / torch.sqrt(1 + z.square().sum(-1, keepdim=True))
        return self.readout(z.flatten(1)), z

    def forward(self, tokens: torch.Tensor, state: torch.Tensor | None = None,
                hops: int | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        if state is None:
            state = torch.zeros(tokens.shape[0], self.config.nodes, 2)
        outputs = []
        for t in range(tokens.shape[1]):
            logits, state = self.step(tokens[:, t], state, hops)
            outputs.append(logits)
        return torch.stack(outputs, 1), state


class WaveLearner:
    """Learning belongs to the model, not a teacher that edits its parameters.

    Transient sequence state is reset between documents/questions and detached
    at truncated backpropagation boundaries. It is not infinite context.
    """

    def __init__(self, config: WaveConfig = WaveConfig()) -> None:
        self.config = config
        torch.set_num_threads(config.threads)
        with torch.random.fork_rng():
            torch.manual_seed(config.seed)
            self.network = WaveNetwork(config)
        self.optimizer = torch.optim.Adam(self.network.parameters(), lr=config.learning_rate)
        self.updates = 0
        self.bytes_seen = 0

    def fingerprint(self) -> str:
        digest = hashlib.sha256()
        for name, value in self.network.state_dict().items():
            digest.update(name.encode())
            digest.update(value.detach().contiguous().numpy().tobytes())
        return digest.hexdigest()

    def learn(self, text: str, *, answer_start: int = 0,
              callback: Callable[[dict], bool] | None = None) -> dict:
        """Learn one supplied text. answer_start is a UTF-8 BYTE boundary.

        For corrections only the supplied answer/explanation is supervised;
        generated answers are never passed back as ground truth automatically.
        callback=False interrupts safely between bounded optimizer updates.
        """
        data = text.encode("utf-8")
        if len(data) > 1_000_000 or not 0 <= answer_start <= len(data):
            raise ValueError("Lesson or answer boundary exceeds the budget.")
        if len(data) < 2:
            return {"loss": None, "tokens": 0, "interrupted": False}
        self.network.train()
        losses, count, state = 0.0, 0, None
        values = torch.tensor(list(data), dtype=torch.long)
        for offset in range(0, len(data) - 1, self.config.sequence_length):
            end = min(offset + self.config.sequence_length, len(data) - 1)
            x, target = values[offset:end][None], values[offset + 1:end + 1][None]
            self.optimizer.zero_grad(set_to_none=True)
            logits, state = self.network(x, state)
            first = max(0, answer_start - offset - 1)
            if first < target.shape[1]:
                loss = F.cross_entropy(logits[:, first:].reshape(-1, 256),
                                       target[:, first:].reshape(-1))
                if not torch.isfinite(loss):
                    raise ArithmeticError("Non-finite learning loss; update not applied.")
                loss.backward()
                norm = nn.utils.clip_grad_norm_(self.network.parameters(), 1.0,
                                               error_if_nonfinite=True)
                self.optimizer.step()
                self.updates += 1
                used = target.shape[1] - first
                losses += float(loss.detach()) * used
                count += used
                self.bytes_seen += used
                if callback and callback({"loss": float(loss.detach()), "tokens": used,
                                          "update": self.updates,
                                          "gradient_norm": float(norm)}) is False:
                    return {"loss": losses / count, "tokens": count, "interrupted": True}
            state = state.detach()
        return {"loss": losses / count if count else None, "tokens": count,
                "interrupted": False}

    def learn_answers(self, examples: list[tuple[str, str]], callback=None) -> dict:
        """Train 1..4 independent answer-focused examples as a balanced batch.

        Prefixes condition the network and receive gradients through the full
        bounded example. Only supplied answer bytes are scored. No generated
        model output is used as a target. Batch rows never share hidden state.
        """
        if not 1 <= len(examples) <= 4:
            raise ValueError("Answer-learning batch must contain 1..4 examples.")
        encoded = []
        for prefix, answer in examples:
            p, a = prefix.encode("utf-8"), (answer + "\n").encode("utf-8")
            if not p or not answer or len(p + a) > 256:
                raise ValueError("An answer example needs a prefix and answer within 256 UTF-8 bytes.")
            encoded.append((p, a))
        length = max(len(p) + len(a) - 1 for p, a in encoded)
        x = torch.zeros(len(encoded), length, dtype=torch.long)
        target = torch.full_like(x, -100)
        for row, (p, a) in enumerate(encoded):
            values = torch.tensor(list(p + a), dtype=torch.long)
            x[row, :len(values)-1] = values[:-1]
            target[row, len(p)-1:len(values)-1] = values[len(p):]
        self.network.train()
        self.optimizer.zero_grad(set_to_none=True)
        logits, _ = self.network(x)
        per_token = F.cross_entropy(logits.transpose(1, 2), target, ignore_index=-100, reduction="none")
        mask = target != -100
        loss = (per_token.sum(1) / mask.sum(1)).mean()
        if not torch.isfinite(loss):
            raise ArithmeticError("Non-finite answer loss; update not applied.")
        loss.backward()
        norm = nn.utils.clip_grad_norm_(self.network.parameters(), 1.0, error_if_nonfinite=True)
        self.optimizer.step()
        self.updates += 1
        used = int(mask.sum())
        self.bytes_seen += used
        event = {"loss": float(loss.detach()), "tokens": used, "update": self.updates,
                 "gradient_norm": float(norm), "objective": "balanced-answer-only",
                 "batch_size": len(examples)}
        interrupted = callback(event) is False if callback else False
        return {**event, "interrupted": interrupted}

    @torch.no_grad()
    def measure(self, text: str) -> dict:
        """Read-only next-byte evaluation; NOT a comprehension or exam score."""
        data = text.encode("utf-8")
        if not 2 <= len(data) <= 1_000_000:
            raise ValueError("Evaluation needs 2..1,000,000 bytes.")
        self.network.eval()
        values = torch.tensor(list(data), dtype=torch.long)
        total_loss, correct, count, state = 0.0, 0, 0, None
        for offset in range(0, len(data) - 1, self.config.sequence_length):
            end = min(offset + self.config.sequence_length, len(data) - 1)
            target = values[offset + 1:end + 1]
            logits, state = self.network(values[offset:end][None], state)
            total_loss += float(F.cross_entropy(logits[0], target, reduction="sum"))
            correct += int((logits[0].argmax(-1) == target).sum())
            count += len(target)
        return {"next_byte_accuracy": correct / count,
                "bits_per_byte": total_loss / count / math.log(2), "bytes": count}

    @torch.no_grad()
    def generate(self, prompt: str, *, max_bytes: int = 64, hops: int | None = None,
                 on_token: Callable[[bytes], None] | None = None) -> str:
        if not prompt or len(prompt.encode("utf-8")) > 4096 or not 1 <= max_bytes <= 256:
            raise ValueError("Prompt/output exceeds the bounded interaction budget.")
        if hops is not None and not 1 <= hops <= self.config.hops:
            raise ValueError("Invalid traversal length.")
        self.network.eval()
        tokens = torch.tensor(list(prompt.encode("utf-8")), dtype=torch.long)[None]
        logits, state = self.network(tokens, hops=hops)
        output = bytearray()
        for _ in range(max_bytes):
            value = int(logits[0, -1].argmax())
            output.append(value)
            if on_token:
                on_token(bytes([value]))
            if value == 10:
                break
            logits, state = self.network(torch.tensor([[value]]), state, hops=hops)
        return output.decode("utf-8", errors="replace").rstrip("\r\n")

    def trace(self) -> dict:
        """Actual learned edge parameters; not hidden prose reasoning."""
        net = self.network
        with torch.no_grad():
            strength = net.edge_logits.softmax(-1) * net.conductance.sigmoid()
            indices = strength.flatten().topk(min(12, strength.numel())).indices
            edges = []
            for idx in indices.tolist():
                destination, slot = divmod(idx, self.config.fan_in)
                edges.append({"from": int(net.sources[destination, slot]),
                              "to": destination, "strength": float(strength[destination, slot]),
                              "phase": float(net.phase[destination, slot])})
        return {"nodes": self.config.nodes, "links": net.sources.numel(),
                "hops": self.config.hops, "updates": self.updates, "edges": edges,
                "note": "Strongest learned base links; actual gates also depend on activity."}

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        torch.save({"schema": 1, "config": asdict(self.config),
                    "network": self.network.state_dict(),
                    "optimizer": self.optimizer.state_dict(), "updates": self.updates,
                    "bytes_seen": self.bytes_seen}, temporary)
        atomic_replace(temporary, path)

    @classmethod
    def load(cls, path: Path) -> "WaveLearner":
        raw = torch.load(path, map_location="cpu", weights_only=True)
        if raw["schema"] != 1:
            raise ValueError("Unknown wave checkpoint schema.")
        learner = cls(WaveConfig(**raw["config"]))
        learner.network.load_state_dict(raw["network"], strict=True)
        learner.optimizer.load_state_dict(raw["optimizer"])
        learner.updates, learner.bytes_seen = raw["updates"], raw["bytes_seen"]
        return learner

    def ledger(self) -> dict:
        parameters = sum(p.numel() for p in self.network.parameters())
        optimizer_bytes = sum(v.numel() * v.element_size()
                              for s in self.optimizer.state.values()
                              for v in s.values() if isinstance(v, torch.Tensor))
        return {"parameters": parameters, "parameter_bytes": parameters * 4,
                "optimizer_bytes": optimizer_bytes, "device": "cpu",
                "threads": self.config.threads, "nodes": self.config.nodes,
                "links": self.config.nodes * self.config.fan_in,
                "bytes_seen": self.bytes_seen, "updates": self.updates,
                "transcripts_in_checkpoint": False, "infinite_memory": False}
