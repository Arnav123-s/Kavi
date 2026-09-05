"""Finite, verifier-gated configuration search; no live model mutation."""

import copy

import torch

from .repair_trials import RepairLearner


def interpolate_candidate(parent, proposal, fraction):
    """Test a smaller learned change; arbitrary topology rewrites are rejected."""
    if not 0 <= fraction <= 1:
        raise ValueError("Interpolation fraction must lie in [0, 1].")
    if (parent.config.nodes, parent.config.fan_in, parent.config.hops) != (
            proposal.config.nodes, proposal.config.fan_in, proposal.config.hops):
        raise ValueError("Only shape-compatible proposals may be interpolated.")
    candidate = (RepairLearner.from_parent(parent, mode="adapter_joint", slots=proposal.network.repair_slots)
                 if isinstance(proposal, RepairLearner) else copy.deepcopy(parent))
    source = dict(proposal.network.named_parameters())
    reference_buffers = dict(proposal.network.named_buffers())
    for name, buffer in candidate.network.named_buffers():
        if name not in reference_buffers or not torch.equal(buffer, reference_buffers[name]):
            raise ValueError("Interpolation cannot silently alter discrete connectivity.")
    with torch.no_grad():
        for name, parameter in candidate.network.named_parameters():
            if name not in source or parameter.shape != source[name].shape:
                raise ValueError("Proposal parameters are incompatible.")
            parameter.lerp_(source[name], fraction)
    # The candidate inherits proposal ancestry, but search makes no Adam steps.
    candidate.updates, candidate.bytes_seen = proposal.updates, proposal.bytes_seen
    # Interpolation does not have a unique corresponding Adam moment history.
    # These are inference-test checkpoints, not a live resumption decision.
    candidate.optimizer = torch.optim.Adam((p for p in candidate.network.parameters() if p.requires_grad),
                                           lr=candidate.config.learning_rate)
    return candidate


def lost_correct_answers(baseline, candidate):
    before = {q["key"] for group in baseline.values() for q in group["outputs"] if q["correct"]}
    after = {q["key"] for group in candidate.values() for q in group["outputs"] if q["correct"]}
    return sorted(before - after)


def primary_correct(scores):
    return sum(group["correct"] for name, group in scores.items() if name.startswith("primary_"))
