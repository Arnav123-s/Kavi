"""Resumable original-book teaching with live observation and interaction.

The teacher never edits learned tensors. It selects admitted material, presents
feedback, grades frozen answers, and advances only through passed prerequisites.
The new text circuit is not credited with the older symbolic core's results.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import codecs
import hashlib
import json
from pathlib import Path
import time

from .book_curriculum import Question, UNITS, load_book, questions, split_paragraphs
from .composition_evaluation import final_audit_manifest
from .pathway_circuit import CircuitState, PathwayCircuitCore
from .pathway_live import LiveEventBus, _safe_write_json
from .wave_core import WaveConfig, WaveLearner


@dataclass(frozen=True)
class TeachingConfig:
    run_dir: Path
    foundation: Path
    resume: Path | None = None
    max_rounds: int = 12
    exam_cases: int = 32
    practice_cases: int = 32
    seed: int = 4301
    keep_available: bool = False
    rest_ms: int = 10
    max_seconds: int = 86400

    def __post_init__(self) -> None:
        if not 1 <= self.max_rounds <= 48 or not 4 <= self.exam_cases <= 128:
            raise ValueError("Invalid teaching or evaluation budget.")
        if not 1 <= self.practice_cases <= 128 or not 0 <= self.rest_ms <= 1000:
            raise ValueError("Invalid practice or pacing budget.")
        if not 10 <= self.max_seconds <= 86400:
            raise ValueError("A run lasts at most 24 hours; explicitly resume afterward.")


class ContinuousTeacher:
    def __init__(self, repo: Path, config: TeachingConfig, bus: LiveEventBus) -> None:
        self.repo, self.config, self.bus = repo.resolve(), config, bus
        self.root = config.run_dir.resolve()
        if not self.root.is_relative_to(self.repo / "runs"):
            raise ValueError("Training artifacts must remain under ignored runs/.")
        self.record, self.sections = load_book(self.repo, self.repo / "curriculum/arithmetic-original.json")
        self.started = time.monotonic()
        self.stopping = False
        self.in_request = False
        self.last_event = 0.0
        self.last_save = time.monotonic()
        self.progress = {"schema": 1, "unit_index": 0, "round": 0, "completed": [],
                         "seen_questions": [], "retention": {}, "history": [],
                         "source_sha256": self.record["sha256"],
                         "teaching_config": {"max_rounds": config.max_rounds,
                            "exam_cases": config.exam_cases, "practice_cases": config.practice_cases,
                            "seed": config.seed}}
        self.core = WaveLearner(WaveConfig(seed=config.seed))
        if config.resume:
            pointer = json.loads((config.resume / "current.json").read_text(encoding="utf-8"))
            folder = (config.resume / pointer["snapshot"]).resolve()
            if not folder.is_relative_to(config.resume.resolve() / "snapshots"):
                raise ValueError("Invalid resume snapshot path.")
            model = folder / "learner.pt"
            if hashlib.sha256(model.read_bytes()).hexdigest() != pointer["sha256"]:
                raise ValueError("Resume checkpoint fingerprint mismatch.")
            self.core = WaveLearner.load(model)
            self.progress = json.loads((folder / "teacher.json").read_text(encoding="utf-8"))
            if self.progress["source_sha256"] != self.record["sha256"]:
                raise ValueError("A changed source needs a new reviewed run.")
            if self.progress["teaching_config"]["seed"] != config.seed:
                raise ValueError("Resume must preserve the original split/exam seed.")
        self.progress.setdefault("sessions", []).append({
            "run_dir": str(self.root), "resume_of": str(config.resume) if config.resume else None,
            "max_rounds": config.max_rounds, "exam_cases": config.exam_cases,
            "practice_cases": config.practice_cases, "max_seconds": config.max_seconds,
            "seed": config.seed, "resumed_incomplete_round_may_repeat": True})
        self.seen = set(self.progress["seen_questions"])
        foundation_data = config.foundation.read_bytes()
        self.foundation = PathwayCircuitCore(CircuitState.from_mapping(json.loads(foundation_data)))
        self.foundation_digest = hashlib.sha256(foundation_data).hexdigest()
        (self.root / "foundation-state.json").write_bytes(foundation_data)
        self.foundation_check()
        self.inbox = self.root / "inbox"
        self.inbox.mkdir(exist_ok=True)
        (self.root / "responses").mkdir(exist_ok=True)
        self.emit("lessons", "lineage", "Kavi: continuing with an internally trainable text circuit.\n"
                  "The preserved symbolic model is checked separately. No language transfer is assumed.\n"
                  f"Original source: {self.record['author']} — {self.record['title']}\n"
                  "All book text and conversation logs stay in this private local run.")
        self.save("initial")

    def emit(self, channel: str, kind: str, display: str, **values) -> None:
        self.bus.emit(channel, kind, display=display, timestamp=time.time(), **values)

    def foundation_check(self) -> None:
        score = self.foundation.evaluate_compositions(final_audit_manifest(seed=20260905, harder=True))
        if score.errors:
            raise ValueError("The saved symbolic foundation failed its earlier retention audit.")
        self.emit("grading", "foundation-retention", "Preserved symbolic foundation: 64/64.\n"
                  "This is a separate structured-program test, not the text model's English score.")

    def save(self, reason: str) -> None:
        self.progress["seen_questions"] = sorted(self.seen)
        name = f"snapshot-{time.time_ns()}"
        folder = self.root / "snapshots" / name
        self.core.save(folder / "learner.pt")
        _safe_write_json(folder / "teacher.json", self.progress)
        _safe_write_json(self.root / "current.json", {
            "snapshot": f"snapshots/{name}", "reason": reason,
            "sha256": hashlib.sha256((folder / "learner.pt").read_bytes()).hexdigest(),
            "foundation_sha256": self.foundation_digest,
            "ledger": self.core.ledger(), "completed": self.progress["completed"],
            "unit_index": self.progress["unit_index"], "round": self.progress["round"],
            "resume_of": str(self.config.resume) if self.config.resume else None})
        self.last_save = time.monotonic()

    def control(self, *, process_requests: bool = True) -> bool:
        if (self.root / "stop").exists() or time.monotonic() - self.started >= self.config.max_seconds:
            self.stopping = True
            return False
        if (self.root / "pause").exists():
            self.save("paused")
            self.bus.update_status("paused", detail="No learning while paused; resume or stop from Chat.")
            while (self.root / "pause").exists():
                if (self.root / "stop").exists() or time.monotonic() - self.started >= self.config.max_seconds:
                    self.stopping = True
                    return False
                time.sleep(0.2)
        if process_requests and not self.in_request:
            self.process_requests()
        if time.monotonic() - self.last_save > 180:
            self.save("periodic")
        return not self.stopping

    def on_update(self, event: dict) -> bool:
        # No reentrant optimizer step from a conversation during a text batch.
        if not self.control(process_requests=False):
            return False
        if time.monotonic() - self.last_event >= 2:
            self.last_event = time.monotonic()
            self.emit("learning", "internal-update",
                      f"Internal update {event['update']} | prediction loss {event['loss']:.4f}\n"
                      "Kavi changed its own encodings, link strengths, gates and phases. Size is unchanged.",
                      **event, ledger=self.core.ledger())
            trace = self.core.trace()
            drawing = "\n".join(f"  {e['from']:02d} -> {e['to']:02d}  strength={e['strength']:.4f} phase={e['phase']:+.3f}"
                                for e in trace["edges"])
            self.emit("pathways", "learned-links", f"{trace['nodes']} mixing points / {trace['links']} available links\n"
                      f"{drawing}\nMeasured base connections; these are not written-out thoughts.", trace=trace)
            self.bus.update_status("learning", unit_index=self.progress["unit_index"],
                                   round=self.progress["round"], updates=self.core.updates,
                                   completed=self.progress["completed"], loss=event["loss"])
        if self.config.rest_ms:
            time.sleep(self.config.rest_ms / 1000)
        return True

    def teach_question(self, q: Question, *, mistake: str | None = None) -> None:
        self.seen.add(q.key)
        self.emit("lessons", "correction" if mistake is not None else "practice",
                  f"{'Correction' if mistake is not None else 'Practice'}: {q.prompt}\n"
                  f"Supplied answer: {q.answer}\nWhy: {q.explanation}\n"
                  "This exercise is teacher-generated from the admitted mathematical topic, not a quote.",
                  previous_answer=mistake)
        text = q.prefix + q.answer + "\nExplanation: " + q.explanation + "\n"
        self.core.learn(text, answer_start=len(q.prefix.encode()), callback=self.on_update)

    def exam(self, unit: str, round_number: int, *, harder: bool = False,
             fixed: list[Question] | None = None, hops: int | None = None) -> tuple[float, list, list]:
        examples = fixed or questions(unit, self.config.seed + round_number * 7919 + (900001 if harder else 1701),
                                     self.config.exam_cases, harder=harder, exclude=self.seen)
        before = self.core.fingerprint()
        self.seen.update(q.key for q in examples)
        errors, outputs = [], []
        partition = "retention" if fixed else "harder-fresh" if harder else "fresh-calibration"
        for i, q in enumerate(examples, 1):
            if not self.control(process_requests=False):
                break
            output = self.core.generate(q.prefix, max_bytes=24, hops=hops)
            outputs.append(output)
            good = q.correct(output)
            if not good:
                errors.append((q, output))
            self.emit("grading", "english-exam", f"{unit}: {partition}, question {i}/{len(examples)}\n"
                      f"Question: {q.prompt}\nKavi: {output!r}\nCorrect: {q.answer}\n"
                      f"{'PASS' if good else 'WRONG'}; score so far {(i-len(errors))/i:.1%}",
                      question=q.prompt, actual=output, expected=q.answer, correct=good,
                      partition=partition, language="en")
            self.emit("answers", "exam-answer", f"{q.prompt}\nKavi: {output!r}\nChecked answer: {q.answer}")
        if before != self.core.fingerprint():
            raise AssertionError("Learning occurred during a supposedly frozen exam.")
        score = (len(outputs) - len(errors)) / len(examples)
        self.emit("grading", "exam-total", f"{unit} | {partition}: {score:.1%}. Required: 90%.\n"
                  "This checks a narrow English arithmetic skill, not a complete subject or degree.", score=score)
        return score, errors, examples

    def retained_skills_pass(self) -> bool:
        for unit, stored in self.progress["retention"].items():
            score, _, _ = self.exam(unit, self.progress["round"],
                                    fixed=[Question(**item) for item in stored])
            if score < 0.9 or self.stopping:
                return False
        return True

    def process_requests(self) -> None:
        for path in sorted(self.inbox.glob("*.json"))[:4]:
            self.in_request = True
            response = {"status": "failed"}
            try:
                if path.stat().st_size > 32768:
                    raise ValueError("Request is too large.")
                request = json.loads(path.read_text(encoding="utf-8"))
                question = str(request["question"])
                if not question or len(question.encode()) > 3000:
                    raise ValueError("Question is empty or too long.")
                self.emit("answers", "conversation-start", f"You: {question}\nKavi: ", request_id=path.stem)
                decoder = codecs.getincrementaldecoder("utf-8")("replace")

                def token(piece: bytes) -> None:
                    self.bus.emit("answers", "stream-token", text=decoder.decode(piece), request_id=path.stem)

                output = self.core.generate(f"Question: {question}\nAnswer: ", max_bytes=128, on_token=token)
                tail = decoder.decode(b"", final=True)
                self.bus.emit("answers", "stream-token", text=tail + "\n", request_id=path.stem)
                self.core.save(self.root / "before-conversation.pt")
                # Input is an observation, not verified truth. Never teach the generated answer.
                self.core.learn(question + "\n", callback=self.on_update)
                if request.get("answer") is not None:
                    answer = str(request["answer"])
                    explanation = str(request.get("explanation", "User-supplied correction; not independently verified."))
                    if len((answer + explanation).encode()) > 8000:
                        raise ValueError("Correction is too long.")
                    self.teach_question(Question(question, answer, explanation), mistake=output)
                accepted = self.retained_skills_pass()
                if not accepted:
                    self.core = WaveLearner.load(self.root / "before-conversation.pt")
                    self.emit("learning", "conversation-rollback",
                              "Conversation update failed a previously passed skill; restored prior parameters.")
                response = {"status": "answered", "question": question, "answer": output,
                            "learning": "input observation and any supplied correction; not self-generated answer",
                            "updates": self.core.updates, "accepted": accepted}
                self.save("conversation")
            except (ValueError, KeyError, TypeError) as error:
                response["error"] = str(error)
            finally:
                _safe_write_json(self.root / "responses" / path.name, response)
                processed = self.root / "processed"
                processed.mkdir(exist_ok=True)
                path.replace(processed / path.name)
                self.in_request = False

    def run(self) -> dict:
        for index in range(self.progress["unit_index"], len(UNITS)):
            unit, title, section = UNITS[index]
            self.progress["unit_index"] = index
            split = split_paragraphs(self.sections[unit], self.config.seed + index)
            _safe_write_json(self.root / f"split-{unit}.json", {
                group: [hashlib.sha256(p.encode()).hexdigest() for p in values]
                for group, values in split.items()})
            self.emit("lessons", "unit-start", f"Lesson {index+1}/{len(UNITS)}: {title}\n"
                      f"Original English source: Book I, Section {section}.\n"
                      f"{len(split['train'])} teaching paragraphs, {len(split['remediation'])} additional paragraphs, "
                      f"{len(split['validation'])} withheld paragraphs.\n"
                      "Only passed prerequisites unlock the next lesson.")
            advanced = False
            for round_number in range(self.progress["round"], self.config.max_rounds):
                self.progress["round"] = round_number
                if not self.control():
                    break
                source_texts = split["train"] if round_number % 2 == 0 else split["remediation"]
                self.core.save(self.root / "before-round.pt")
                for number, paragraph in enumerate(source_texts, 1):
                    if not self.control():
                        break
                    self.emit("lessons", "original-passage", f"{title} | teaching round {round_number+1} | "
                              f"passage {number}/{len(source_texts)}\n{paragraph}",
                              source_id=self.record["source_id"], language=self.record["language"], translated=False)
                    self.core.learn(paragraph + "\n", callback=self.on_update)
                if self.stopping:
                    break
                practice = questions(unit, self.config.seed + 31000 + round_number * 3571,
                                     self.config.practice_cases, exclude=self.seen)
                for q in practice:
                    if not self.control():
                        break
                    self.teach_question(q)
                if self.stopping:
                    break
                measures = self.core.measure("\n\n".join(split["validation"])[:4000])
                self.emit("grading", "text-prediction", f"Withheld original paragraphs: "
                          f"next-byte accuracy {measures['next_byte_accuracy']:.1%}, "
                          f"{measures['bits_per_byte']:.3f} bits/byte.\n"
                          "Text prediction is NOT counted as understanding or a mastery pass.", **measures)
                score, errors, examples = self.exam(unit, round_number)
                retention_ok = True
                for old_unit, stored in self.progress["retention"].items():
                    old_examples = [Question(**item) for item in stored]
                    old_score, _, _ = self.exam(old_unit, round_number, fixed=old_examples)
                    retention_ok &= old_score >= 0.9
                if not retention_ok:
                    self.core = WaveLearner.load(self.root / "before-round.pt")
                    self.emit("learning", "rollback", "The new configuration damaged a passed skill. "
                              "Restored the pre-round configuration; the failed result stays in the log.")
                elif score >= 0.9 and not self.stopping:
                    hard_score, hard_errors, harder_examples = self.exam(unit, round_number, harder=True)
                    errors.extend(hard_errors)
                    if hard_score >= 0.9 and not self.stopping:
                        self.progress["retention"][unit] = [asdict(q) for q in examples + harder_examples]
                        self.progress["completed"].append(unit)
                        self.progress["unit_index"], self.progress["round"] = index + 1, 0
                        self.save("mastery-passed")
                        advanced = True
                        break
                if self.stopping:
                    break
                # Once used for feedback, a calibration question is no longer unseen.
                for q, wrong in errors:
                    if not self.control():
                        break
                    self.teach_question(q, mistake=wrong)
                if not self.stopping and not self.retained_skills_pass():
                    self.core = WaveLearner.load(self.root / "before-round.pt")
                    retention_ok = False
                    self.emit("learning", "feedback-rollback",
                              "Corrections damaged a previously passed skill; restored the pre-round configuration.")
                self.progress["history"].append({"unit": unit, "round": round_number,
                                                 "english_score": score, "prediction": measures,
                                                 "retention_ok": retention_ok})
                self.progress["round"] = round_number + 1
                self.save("round-completed")
                if self.stopping:
                    break
            if not advanced:
                break
        self.save("stopped" if self.stopping else "teaching-budget-boundary")
        if not self.stopping and self.config.keep_available:
            boundary = "More teaching is needed. The automatic round budget is exhausted; "
            if len(self.progress["completed"]) == len(UNITS):
                boundary = "All implemented arithmetic units passed. Broader source/exam lanes need implementation; "
            self.emit("lessons", "awaiting-teaching", boundary +
                      "Kavi remains available in Chat for questions and corrections. "
                      "Waiting is not counted as training or progress.")
            while self.control():
                self.bus.update_status("awaiting-teaching", completed=self.progress["completed"],
                                       unit_index=self.progress["unit_index"], round=self.progress["round"],
                                       detail=boundary, updates=self.core.updates)
                time.sleep(0.25)
        self.foundation_check()
        self.save("run-ended")
        summary = {"completed": self.progress["completed"], "unit_index": self.progress["unit_index"],
                   "round": self.progress["round"], "ledger": self.core.ledger(),
                   "masters_level_demonstrated": False, "english_understanding_demonstrated": False,
                   "symbolic_and_text_transfer_demonstrated": False,
                   "seconds": time.monotonic() - self.started}
        _safe_write_json(self.root / "report.json", summary)
        self.bus.update_status("stopped" if self.stopping else "complete", **summary)
        return summary
