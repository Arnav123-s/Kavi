"""Language-first, prerequisite-gated teaching of the actual local text core.

Examples are classroom exercises, not original-author quotations. Familiar
practice, new tests, and protected retention are separate measurements. This
controller cannot promote unimplemented languages or claim degree-level skill.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import random
import shutil
import time

from .book_curriculum import Question, UNITS, questions, split_paragraphs
from .continuous_teacher import ContinuousTeacher
from .language_curriculum import LanguageExample, LanguageStage, STAGES, inventory, varied
from .pathway_live import _safe_write_json
from .teaching_sources import TeachingSources
from .wave_core import WaveLearner


def school_stages() -> tuple[LanguageStage, ...]:
    stages = list(STAGES)
    for unit, title, _ in UNITS:
        stages.append(LanguageStage("math-" + unit, title, (stages[-1].stage_id,), (),
                                    "A narrow English arithmetic task; not a complete subject qualification."))
    return tuple(stages)


class LanguageFirstTeacher(ContinuousTeacher):
    def __init__(self, repo, config, bus):
        super().__init__(repo, config, bus)
        self.sources = TeachingSources(self.repo, self.repo / "curriculum/language-source-packets.json")
        self.stages = school_stages()
        self.school = self.progress.setdefault("language_first", {
            "schema": 1, "stage_index": 0, "round": 0, "passed": [], "retention": {},
            "letter_count": 4, "history": [], "source_packets_seen": [],
            "catalog_sha256": self.sources.catalog_hash,
            "scope": "Five controlled English foundations, then nine arithmetic skills. Other languages and advanced fields are not implemented here."})
        if self.school["catalog_sha256"] != self.sources.catalog_hash:
            raise ValueError("Changed language source catalog requires an explicit migration/review.")
        self.emit("lessons", "language-first-order",
                  "Corrected order: letters -> written words -> small number meanings -> sentences -> passages -> arithmetic.\n"
                  "Old arithmetic attempts remain in the checkpoint; they do not bypass these prerequisites.\n"
                  "A 90% familiar score alone is insufficient: new questions, harder new questions and retention must also pass.")
        self.save("language-first-initial")

    @staticmethod
    def prompt_prefix(question: str) -> str:
        return question + " => "

    def current_stage(self):
        index = self.school["stage_index"]
        return self.stages[index] if index < len(self.stages) else None

    def on_update(self, event):
        result = super().on_update(event)
        stage = self.current_stage()
        if stage:
            self.bus.update_status("learning", stage=stage.stage_id, lesson=stage.title,
                                   round=self.school["round"] + 1, passed=self.school["passed"],
                                   letter_count=self.school["letter_count"], updates=self.core.updates,
                                   loss=event["loss"], objective=event.get("objective", "source-text"))
        return result

    def teach_question(self, q, *, mistake=None):
        self.teach_examples([q], mistake=mistake)

    def teach_examples(self, examples, *, mistake=None, epochs=1):
        # Feedback is visible, but the answer objective is not drowned in prose.
        for q in examples:
            self.seen.add(q.key)
            self.emit("lessons", "correction" if mistake is not None else "practice",
                      f"Teach: {q.prompt}\nCorrect answer: {q.answer}\nWhy: {q.explanation}\n"
                      "Teacher-generated exercise, derived from the reviewed lesson; not an author quotation.",
                      previous_answer=mistake)
        rng = random.Random(self.config.seed + self.core.updates)
        for _ in range(epochs):
            rows = list(examples)
            rng.shuffle(rows)  # Only within the unlocked lesson; never shuffle prerequisites.
            for start in range(0, len(rows), 4):
                if not self.control():
                    return
                batch = [(self.prompt_prefix(q.prompt), q.answer) for q in rows[start:start+4]]
                if any(len((p + a + "\n").encode()) > 256 for p, a in batch):
                    # Long owner corrections retain the existing bounded-text path.
                    for prefix, answer in batch:
                        self.core.learn(prefix + answer + "\n", answer_start=len(prefix.encode()),
                                        callback=self.on_update)
                else:
                    self.core.learn_answers(batch, callback=self.on_update)

    def known_examples(self, stage):
        if stage.stage_id.startswith("math-"):
            return questions(stage.stage_id[5:], self.config.seed + 77, self.config.exam_cases)
        rows = inventory(stage.stage_id)
        if stage == STAGES[0]:
            return rows[:self.school["letter_count"]]
        return rows

    def new_examples(self, stage, *, harder=False, practice=False):
        seed = self.config.seed + self.school["round"] * 7919 + (900001 if harder else 1701)
        if practice:
            seed += 31000
        count = self.config.practice_cases if practice else self.config.exam_cases
        excluded = None if practice else self.seen
        if stage.stage_id.startswith("math-"):
            return questions(stage.stage_id[5:], seed, count, harder=harder, exclude=excluded)
        return varied(stage.stage_id, seed, count, harder=harder, exclude=excluded)

    def source_lesson(self, stage):
        if stage.source_packets:
            packet_id = stage.source_packets[self.school["round"] % len(stage.source_packets)]
            try:
                text, packet, fetched = self.sources.packet(packet_id)
            except (OSError, ValueError) as error:
                self.emit("lessons", "source-unavailable",
                          f"Reviewed source unavailable: {error}. No substitute or unreviewed download was used.")
                retry_at = time.monotonic() + 30
                self.bus.update_status("source-unavailable", detail=str(error), retry_seconds=30)
                while time.monotonic() < retry_at and self.control():
                    time.sleep(0.2)
                return False
            self.school["source_packets_seen"] = sorted(set(self.school["source_packets_seen"]) | {packet_id})
            self.emit("lessons", "original-source",
                      f"Original source: {packet['source_id']} | {packet['locator']}\n{text}\n"
                      f"{'Fetched and fingerprint-checked' if fetched else 'Reused verified local source'}; not a translation.\n"
                      "At the letter stage this is a teacher reference, not evidence that Kavi understands the passage.",
                      source_id=packet["source_id"], translated=False, fetched=fetched,
                      extract_sha256=hashlib.sha256(text.encode()).hexdigest())
            if stage != STAGES[0] and self.school["round"] % 4 == 0:
                self.core.learn(text + "\n", callback=self.on_update)
        else:
            unit = stage.stage_id[5:]
            index = next(i for i, item in enumerate(UNITS) if item[0] == unit)
            split = split_paragraphs(self.sections[unit], self.config.seed + index)
            partition = "remediation" if self.school["round"] % 2 else "train"
            rows = split[partition]
            text = rows[self.school["round"] % len(rows)]
            self.emit("lessons", "original-source", f"De Morgan, original English: {partition} passage\n{text}",
                      source_id=self.record["source_id"], translated=False)
            self.core.learn(text + "\n", callback=self.on_update)
        return True

    def check(self, stage, examples, partition):
        before = self.core.fingerprint()
        errors, correct, outputs = [], [], []
        self.seen.update(q.key for q in examples)
        for i, q in enumerate(examples, 1):
            if not self.control(process_requests=False):
                break
            # Only the question enters the model. The answer remains in the grader.
            actual = self.core.generate(self.prompt_prefix(q.prompt), max_bytes=96)
            outputs.append(actual)
            good = q.correct(actual)
            (correct if good else errors).append(q if good else (q, actual))
            self.emit("answers", "model-answer", f"{q.prompt}\nKavi: {actual!r}\nChecked answer: {q.answer}")
            self.emit("grading", "language-check",
                      f"{stage.title} | {partition} | {i}/{len(examples)}\n"
                      f"Question: {q.prompt}\nKavi: {actual!r}\nExpected: {q.answer}\n"
                      f"{'CORRECT' if good else 'WRONG'} | {len(correct)}/{i}",
                      question=q.prompt, actual=actual, expected=q.answer, correct=good, partition=partition)
        if before != self.core.fingerprint():
            raise AssertionError("An evaluation changed the model.")
        score = len(correct) / len(examples) if examples else 0.0
        complete = len(outputs) == len(examples) and bool(examples)
        common = Counter(outputs).most_common(1)
        concentration = common[0][1] / len(outputs) if common else 0.0
        self.emit("grading", "check-total",
                  f"{stage.title} | {partition}: {score:.1%}. Required: 90%.\n"
                  f"Distinct outputs: {len(set(outputs))}/{len(outputs)}. Most common output share: {concentration:.1%}.\n"
                  f"Scope: {stage.scope}", score=score, complete=complete,
                  distinct_outputs=len(set(outputs)), most_common_share=concentration, partition=partition)
        return score if complete else 0.0, errors, correct

    def retained_skills_pass(self):
        if not hasattr(self, "school"):
            return super().retained_skills_pass()
        for stage_id, stored in self.school["retention"].items():
            stage = next(s for s in self.stages if s.stage_id == stage_id)
            cls = Question if stage_id.startswith("math-") else LanguageExample
            score, _, _ = self.check(stage, [cls(**q) for q in stored], "protected-retention")
            if score < 1.0 or self.stopping:
                return False
        return True

    def remedy(self, stage, errors):
        self.emit("lessons", "remediation-plan",
                  "Not passed. Revisit the prerequisite, show corrections, then practise again.\n"
                  "Corrected test questions will never be presented as new again.")
        if stage.prerequisites:
            prior = next(s for s in self.stages if s.stage_id == stage.prerequisites[-1])
            rows = self.known_examples(prior)
            self.teach_examples(rows, epochs=2)
        # Select another reviewed original packet next round; no arbitrary web crawl.
        for q, actual in errors:
            if not self.control():
                break
            self.teach_question(q, mistake=actual)

    def fresh_check(self, stage, *, harder=False):
        try:
            rows = self.new_examples(stage, harder=harder)
        except ValueError as error:
            if "exhausted" not in str(error).lower():
                raise
            self.emit("grading", "fresh-pool-exhausted",
                      "No unused questions remain in this finite test pool. Continue familiar practice, "
                      "but do not claim a fresh pass. A broader reviewed test family is needed.")
            return None
        return self.check(stage, rows, "harder-unseen" if harder else "unseen")

    def run_round(self, stage):
        if not all(p in self.school["passed"] for p in stage.prerequisites):
            raise ValueError("An unmet prerequisite cannot be bypassed.")
        self.core.save(self.root / 'before-school-round.pt')
        if not self.source_lesson(stage) or self.stopping:
            return
        # The rollback witness is captured before any source or answer update.
        known = self.known_examples(stage)
        self.teach_examples(known, epochs=16 if len(known) <= 8 else 8)
        if self.stopping:
            return
        score, errors, protected = self.check(stage, known, "familiar-practice-not-unseen")
        full_inventory = stage != STAGES[0] or self.school["letter_count"] == len(inventory(stage.stage_id))
        promote, new_score, hard_score = False, None, None
        if score >= 0.9 and not self.stopping:
            if not full_inventory:
                self.school["letter_count"] = min(52, self.school["letter_count"] + 4)
                self.emit("lessons", "next-letters",
                          f"Familiar letters passed; expand to {self.school['letter_count']} letters. "
                          "This is not a new-word or comprehension pass.")
            else:
                result = self.fresh_check(stage)
                if result is not None:
                    new_score, wrong, good = result
                    errors.extend(wrong)
                    protected.extend(good)
                    if new_score >= 0.9 and not self.stopping:
                        harder = self.fresh_check(stage, harder=True)
                        if harder is not None:
                            hard_score, wrong, good = harder
                            errors.extend(wrong)
                            protected.extend(good)
                            promote = hard_score >= 0.9
        if not self.stopping and not self.retained_skills_pass():
            self.core = WaveLearner.load(self.root / "before-school-round.pt")
            promote = False
            self.emit("learning", "retention-rollback", "A passed skill regressed. Restored the previous configuration.")
        if promote and not self.stopping:
            self.school["passed"].append(stage.stage_id)
            # Protect only examples actually answered correctly, not allowed errors.
            self.school["retention"][stage.stage_id] = [asdict(q) for q in protected]
            self.school["stage_index"] += 1
            self.school["round"] = 0
            self.emit("lessons", "stage-passed", f"Passed the measured scope: {stage.scope}\nNext prerequisite is unlocked.")
            self.save("language-first-stage-passed")
            return
        if not self.stopping:
            self.remedy(stage, errors)
            if full_inventory:
                # Familiar practice can be repeated indefinitely without exhausting a test pool.
                self.teach_examples(self.new_examples(stage, practice=True), epochs=2)
            if not self.stopping and not self.retained_skills_pass():
                self.core = WaveLearner.load(self.root / "before-school-round.pt")
                self.emit("learning", "correction-rollback", "Corrections regressed a protected skill; restored the prior configuration.")
        record = {"stage": stage.stage_id, "round": self.school["round"], "familiar_score": score,
                  "unseen_score": new_score, "harder_score": hard_score, "updates": self.core.updates}
        self.school["history"].append(record)
        self.emit("learning", "round-summary", f"Round recorded: {record}", **record)
        self.school["round"] += 1
        # All events are append-only. Durable snapshots every 3 minutes, not every batch.
        if time.monotonic() - self.last_save >= 180:
            self.save("language-first-periodic")

    def run(self):
        rounds = 0
        while self.control():
            if shutil.disk_usage(self.root).free < 2_000_000_000:
                self.emit("lessons", "storage-limit", "Less than 2 GB free. Save and stop before consuming remaining disk space.")
                self.stopping = True
                break
            stage = self.current_stage()
            if stage is None:
                self.emit("lessons", "implemented-syllabus-complete",
                          "All implemented narrow gates passed. No other language or master's-level field is certified. "
                          "Unimplemented sources and exams cannot be skipped or marked passed.")
                break
            self.emit("lessons", "lesson-start", f"Lesson: {stage.title} | attempt {self.school['round'] + 1}\n{stage.scope}")
            self.run_round(stage)
            rounds += 1
            if not self.config.keep_available and rounds >= self.config.max_rounds:
                break
            # With keep_available, failed rounds continue teaching within the explicit session time budget.
        self.save("language-first-ended")
        summary = {"passed": self.school["passed"], "stage_index": self.school["stage_index"],
                   "round": self.school["round"], "ledger": self.core.ledger(),
                   "masters_level_demonstrated": False, "general_english_understanding_demonstrated": False,
                   "all_languages_demonstrated": False, "seconds": time.monotonic() - self.started}
        _safe_write_json(self.root / "report.json", summary)
        self.bus.update_status("stopped" if self.stopping else "complete", **summary)
        return summary
