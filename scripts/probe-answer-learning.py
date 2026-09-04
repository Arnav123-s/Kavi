"""Offline checkpoint probe; never changes the active live model."""

from copy import deepcopy
import json
from pathlib import Path
import sys

import torch
from torch.nn import functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kavi.wave_core import WaveLearner

root = Path(sys.argv[1]).resolve()
pointer = json.loads((root / "current.json").read_text())
model_path = root / pointer["snapshot"] / "learner.pt"
learner = WaveLearner.load(model_path)
questions = ["What is one plus one?", "What is two plus two?",
             "Write five using decimal digits.", "Write nine using decimal digits."]
states, outputs = [], []
with torch.no_grad():
    for question in questions:
        prompt = f"Question: {question}\nAnswer: "
        tokens = torch.tensor(list(prompt.encode()), dtype=torch.long)[None]
        logits, state = learner.network(tokens)
        states.append(state)
        outputs.append({"question": question, "answer": learner.generate(prompt, max_bytes=16),
                        "first_byte_probabilities": {c: float(logits[0, -1].softmax(-1)[ord(c)]) for c in "2459"}})
    distance = [float((states[0] - state).square().mean().sqrt()) for state in states[1:]]
print(json.dumps({"checkpoint_updates": learner.updates, "outputs": outputs,
                  "state_rms_difference_from_first": distance,
                  "memory_gate_min_mean_max": [float(v) for v in (
                      learner.network.memory_gate.sigmoid().min(), learner.network.memory_gate.sigmoid().mean(),
                      learner.network.memory_gate.sigmoid().max())]}, indent=2))

for answer_only in (False, True):
    clone = deepcopy(learner)
    prompt = "Question: What is one plus one?\nAnswer: "
    text = prompt + "2\n"
    if not answer_only:
        text += "Explanation: Addition combines two groups of one into two units.\n"
    for _ in range(12):
        clone.learn(text, answer_start=len(prompt.encode()))
    with torch.no_grad():
        logits, _ = clone.network(torch.tensor(list(prompt.encode()))[None])
        p = float(logits[0, -1].softmax(-1)[ord("2")])
    print(json.dumps({"mode": "answer-only" if answer_only else "answer-plus-explanation",
                      "after_12_examples": clone.generate(prompt, max_bytes=16), "p_correct_first_byte": p}))
