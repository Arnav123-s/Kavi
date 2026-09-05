"""Small contextual residual connections for isolated retention experiments.

The base parameters can remain frozen while a few zero-effect connections
learn. Freezing parameters does not guarantee preservation of the output map.
"""

from dataclasses import asdict
import hashlib

import torch
from torch import nn

from .file_io import atomic_replace
from .pathway_trials import TrialLearner
from .wave_core import WaveConfig, WaveNetwork


class RepairNetwork(WaveNetwork):
    def __init__(self, config, slots=8):
        super().__init__(config)
        if not 1 <= slots <= min(8, config.nodes):
            raise ValueError("Repair capacity is one to eight connections.")
        self.repair_slots = slots
        destinations = torch.arange(slots) * config.nodes // slots
        self.register_buffer("repair_destinations", destinations)
        self.register_buffer("repair_sources", (destinations + 1) % config.nodes)
        self.repair_context = nn.Parameter(torch.randn(slots, 4) * 0.05)
        self.repair_bias = nn.Parameter(torch.zeros(slots))
        self.repair_gain = nn.Parameter(torch.zeros(slots))
        self.repair_phase = nn.Parameter(torch.zeros(slots))

    def step(self, token, state, hops=None):
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
            message = torch.stack(((transmission * (co * real - si * imag)).sum(-1),
                                   (transmission * (si * real + co * imag)).sum(-1)), -1)
            signal = z[:, self.repair_sources, :]
            context = torch.cat((signal, incoming[:, self.repair_destinations, :]), -1)
            activity = torch.sigmoid((context * self.repair_context).sum(-1) + self.repair_bias)
            amplitude = 0.5 * torch.tanh(self.repair_gain) * activity
            pc, ps = self.repair_phase.cos(), self.repair_phase.sin()
            rotated = torch.stack((pc * signal[..., 0] - ps * signal[..., 1],
                                   ps * signal[..., 0] + pc * signal[..., 1]), -1)
            correction = torch.zeros_like(message).index_add(1, self.repair_destinations,
                                                              amplitude[..., None] * rotated)
            z = z + 0.5 * (message + correction) + 0.25 * incoming
            z = z / torch.sqrt(1 + z.square().sum(-1, keepdim=True))
        return self.readout(z.flatten(1)), z


class RepairLearner(TrialLearner):
    @classmethod
    def from_parent(cls, parent, *, mode="adapter_only", slots=8):
        if mode not in ("adapter_only", "adapter_joint"):
            raise ValueError("Unknown repair experiment.")
        child = cls(parent.config)
        with torch.random.fork_rng():
            torch.manual_seed(parent.config.seed + 1909)
            child.network = RepairNetwork(parent.config, slots)
        absent, extra = child.network.load_state_dict(parent.network.state_dict(), strict=False)
        if extra or any(not name.startswith("repair_") for name in absent):
            raise ValueError("Parent and repair network differ outside repair state.")
        child.mode = mode
        child.configure_trainable()
        child.optimizer = torch.optim.Adam((p for p in child.network.parameters() if p.requires_grad),
                                           lr=parent.config.learning_rate)
        if mode == "adapter_joint":
            prior = dict(parent.network.named_parameters())
            for name, parameter in child.network.named_parameters():
                if name in prior:
                    for key, value in parent.optimizer.state[prior[name]].items():
                        child.optimizer.state[parameter][key] = value.clone() if isinstance(value, torch.Tensor) else value
        child.updates, child.bytes_seen = parent.updates, parent.bytes_seen
        return child

    def configure_trainable(self):
        for name, parameter in self.network.named_parameters():
            parameter.requires_grad_(name.startswith("repair_") or
                                     (self.mode == "adapter_joint" and
                                      (name != "phase" or self.config.phase_enabled)))

    def base_fingerprint(self):
        digest = hashlib.sha256()
        for name, value in self.network.state_dict().items():
            if not name.startswith("repair_"):
                digest.update(name.encode())
                digest.update(value.detach().contiguous().numpy().tobytes())
        return digest.hexdigest()

    def ledger(self):
        return {**super().ledger(), "repair_links": self.network.repair_slots,
                "total_links": self.network.sources.numel() + self.network.repair_slots,
                "trainable_parameters": sum(p.numel() for p in self.network.parameters() if p.requires_grad),
                "repair_mode": self.mode}

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        torch.save({"schema": "repair-trial-1", "mode": self.mode,
                    "slots": self.network.repair_slots, "config": asdict(self.config),
                    "network": self.network.state_dict(), "optimizer": self.optimizer.state_dict(),
                    "updates": self.updates, "bytes_seen": self.bytes_seen}, temporary)
        atomic_replace(temporary, path)

    @classmethod
    def load(cls, path):
        raw = torch.load(path, map_location="cpu", weights_only=True)
        if raw["schema"] != "repair-trial-1":
            raise ValueError("Not an experimental repair checkpoint.")
        child = cls(WaveConfig(**raw["config"]))
        with torch.random.fork_rng():
            torch.manual_seed(child.config.seed + 1909)
            child.network = RepairNetwork(child.config, raw["slots"])
        child.mode = raw["mode"]
        child.configure_trainable()
        child.optimizer = torch.optim.Adam((p for p in child.network.parameters() if p.requires_grad),
                                           lr=child.config.learning_rate)
        child.network.load_state_dict(raw["network"])
        child.optimizer.load_state_dict(raw["optimizer"])
        child.updates, child.bytes_seen = raw["updates"], raw["bytes_seen"]
        return child
