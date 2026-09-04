"""A teacher-only curriculum bridge; the learned network is unchanged."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import json
import random
import re
import time

from .language_curriculum import LETTERS, STAGES, LanguageExample, letters_case
from .language_teacher import LanguageFirstTeacher
from .wave_core import WaveLearner
from .mixed_quizzes import mixed_questions, task_name


def reserved_bank(seed, excluded, count=64):
    """Fixed, untrained assessment banks; their repeated use is explicitly labeled."""
    rng, keys, result = random.Random(seed), set(excluded), {}
    for length in (3, 4):
        rows = []
        while len(rows) < count:
            q = letters_case("".join(rng.choice(LETTERS) for _ in range(length)))
            if q.key not in keys:
                rows.append(asdict(q))
                keys.add(q.key)
        result[str(length)] = rows
    return result


def sequence_practice(seed, reserved, count=64, max_length=3):
    rng, result = random.Random(seed), []
    while len(result) < count:
        length = rng.randint(2, max_length)
        q = letters_case("".join(rng.choice(LETTERS) for _ in range(length)))
        if q.key not in reserved:
            result.append(q)
    return result


class MultilingualBridgeTeacher(LanguageFirstTeacher):
    def __init__(self, repo, config, bus):
        super().__init__(repo, config, bus)
        path = self.repo / "curriculum/multilingual-bridge.json"
        self.bridge_catalog = json.loads(path.read_text(encoding="utf-8"))
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source, _ = self.sources.ensure(self.bridge_catalog["source_id"])
        records = {line.split(";")[0]: line.split(";") for line in source.read_text(encoding="utf-8").splitlines()}
        if hashlib.sha256(source.read_bytes()).hexdigest() != self.bridge_catalog["source_sha256"]:
            raise ValueError("The script source fingerprint changed.")
        for lane in self.bridge_catalog["lanes"]:
            for character in lane["characters"]:
                if len(character) != 1:
                    raise ValueError("Each initial script item must be one code point.")
                record = records.get(f"{ord(character):04X}")
                if len(character) != 1 or not record or not record[2].startswith("L"):
                    raise ValueError("A selected script character is not a reviewed letter record.")
        words, _, _ = self.sources.packet(self.bridge_catalog["english_word_packet"])
        for word in self.bridge_catalog["english_copy_words"]:
            if not re.search(r"\b" + re.escape(word) + r"\b", words, re.IGNORECASE):
                raise ValueError("A copy word does not occur in its declared original source packet.")
        self.bridge = self.progress.setdefault("multilingual_bridge", {
            "schema": 1, "catalog_sha256": digest, "cycle": 0, "max_length": 3, "quiz_difficulty": 3, "mixed_quiz_history": [], "pending_feedback": [],
            "banks": reserved_bank(config.seed + 718091, self.seen),
            "lanes": {lane["id"]: {"count": 4, "correct_characters": [], "history": []}
                      for lane in self.bridge_catalog["lanes"]},
            "audit_history": [], "invalidated_bank_keys": [], "policy": "sequence-bridge-v1"})
        if self.bridge["catalog_sha256"] != digest:
            raise ValueError("A changed bridge needs a reviewed migration.")
        self.reserved_keys = {LanguageExample(**q).key for rows in self.bridge["banks"].values() for q in rows}
        self.reserved_sequences = {q['answer'] for rows in self.bridge['banks'].values() for q in rows}
        self.candidate_active = False
        self.topic = "Short sequences and original written forms"
        self.emit("lessons", "bridge-policy",
                  "Small curriculum extension: sequences and copied words, plus Hindi/Devanagari, Arabic and Spanish/Latin writing foundations.\n"
                  "The model and optimizer are preserved. No completed stage is invented. Old exhausted tests remain recorded.\n"
                  "New reserved tests are never selected for automatic teaching; repeated assessments are labeled repeated.")
        self.save("multilingual-bridge-initial")

    def save(self, reason):
        # Do not publish a partially updated candidate as a durable accepted model.
        if getattr(self, "candidate_active", False):
            return
        super().save(reason)

    def process_requests(self):
        # Owner interaction with a reserved question invalidates its assessment use.
        if hasattr(self, "bridge"):
            for path in sorted(self.inbox.glob("*.json"))[:4]:
                if path.stat().st_size > 32768:
                    continue
                try:
                    question = str(json.loads(path.read_text(encoding="utf-8"))["question"])
                    if question.startswith("Copy "):
                        key = letters_case(question[5:]).key
                        if key in self.reserved_keys:
                            self.bridge["invalidated_bank_keys"] = sorted(set(self.bridge["invalidated_bank_keys"]) | {key})
                except (ValueError, KeyError, TypeError):
                    continue
        super().process_requests()

    def teach_examples(self, examples, *, mistake=None, epochs=1):
        if hasattr(self, "reserved_keys"):
            invalid = set(self.bridge["invalidated_bank_keys"])
            for q in examples:
                key = letters_case(q.prompt[5:]).key if q.prompt.startswith("Copy ") else q.key
                if key in self.reserved_keys and key not in invalid:
                    raise ValueError("Reserved assessment question cannot enter automatic teaching.")
        return super().teach_examples(examples, mistake=mistake, epochs=epochs)

    def on_update(self, event):
        result = super().on_update(event)
        if hasattr(self, "bridge"):
            self.bus.update_status("learning", stage=self.current_stage().stage_id if self.current_stage() else None,
                                   lesson=self.topic, cycle=self.bridge["cycle"], updates=self.core.updates,
                                   loss=event["loss"], mode="multilingual-bridge",
                                   sequence_length=self.bridge["max_length"], passed=self.school["passed"],
                                   language_subsets={k: v["count"] for k, v in self.bridge["lanes"].items()})
        return result

    def audit(self, title, rows, *, show_answers=False):
        before = self.core.fingerprint()
        correct, actuals = [], []
        for q in rows:
            if not self.control(process_requests=False):
                break
            actual = self.core.generate(self.prompt_prefix(q.prompt), max_bytes=24)
            good = q.correct(actual)
            if good:
                correct.append(q)
            actuals.append({"question": q.prompt, "actual": actual, "expected": q.answer, "correct": good})
            if show_answers:
                self.emit("answers", "bridge-answer", f"{title}\n{q.prompt}\nKavi: {actual!r}\nExpected: {q.answer} | {'CORRECT' if good else 'WRONG'}")
        if self.core.fingerprint() != before:
            raise AssertionError("Assessment changed model parameters.")
        complete = len(actuals) == len(rows) and bool(rows)
        score = len(correct) / len(rows) if complete else 0.0
        self.emit("grading", "bridge-audit", f"{title}: {len(correct)}/{len(rows)} = {score:.1%}",
                  partition=title, score=score, complete=complete, outputs=actuals, updates=self.core.updates)
        return score, correct

    def retained_skills_pass(self):
        if not super().retained_skills_pass():
            return False
        if not hasattr(self, "bridge"):
            return True
        if self.school["letter_count"] == 52:
            score, _ = self.audit("52 earlier Latin letters: retention only", [letters_case(c) for c in LETTERS])
            if score < 1 or self.stopping:
                return False
        for state in self.bridge["lanes"].values():
            if state["correct_characters"]:
                rows = [letters_case(c) for c in state["correct_characters"]]
                score, _ = self.audit("Previously correct script characters: retention", rows)
                if score < 1 or self.stopping:
                    return False
        return True

    def script_rehearsal(self):
        characters = {c for state in self.bridge["lanes"].values() for c in state["correct_characters"]}
        return [letters_case(c) for c in sorted(characters)]

    def mixed_quiz(self, characters):
        difficulty = self.bridge["quiz_difficulty"]
        try:
            rows = mixed_questions(self.config.seed + 508001 + self.bridge["cycle"] * 7919,
                                   difficulty=difficulty, extra_characters=characters,
                                   exclude=self.seen | self.reserved_keys,
                                   avoid_sequences=self.reserved_sequences)
        except ValueError as error:
            if "unused" not in str(error):
                raise
            self.emit("grading", "mixed-pool-exhausted", "This mixed family is exhausted. No recycled prompt is awarded fresh credit.")
            return
        self.seen.update(q.key for q in rows)
        score, correct = self.audit(f"NEW mixed quiz: copy/join/first/last, length 3..{difficulty}", rows, show_answers=True)
        if self.stopping:
            return
        totals = Counter(task_name(q) for q in rows)
        correct_by_kind = Counter(task_name(q) for q in correct)
        per_task = {kind: correct_by_kind[kind] / total for kind, total in totals.items()}
        record = {"cycle": self.bridge["cycle"], "difficulty": difficulty,
                  "score": score, "per_task": per_task, "updates": self.core.updates}
        self.bridge["mixed_quiz_history"].append(record)
        self.emit("grading", "mixed-quiz-summary", f"Difficulty {difficulty}: {per_task}.\nScores at different difficulties are reported separately.", **record)
        good_keys = {q.key for q in correct}
        self.bridge["pending_feedback"] = [asdict(q) for q in rows if q.key not in good_keys]
        if score >= 0.9 and all(value >= 0.9 for value in per_task.values()):
            self.bridge["quiz_difficulty"] = min(6, difficulty + 1)
            self.emit("lessons", "difficulty-increased", f"Every mixed task met 90%; raise sequence difficulty to {self.bridge['quiz_difficulty']}. This is not a general language-mastery claim.")

    def assessment(self):
        scores = {}
        invalid = set(self.bridge["invalidated_bank_keys"])
        for length, stored in self.bridge["banks"].items():
            rows = [LanguageExample(**q) for q in stored]
            rows = [q for q in rows if q.key not in invalid]
            if len(rows) < 32:
                self.emit("grading", "assessment-invalidated", "Too many reserved cases were exposed to owner teaching; no mastery pass can be awarded.")
                return False
            score, _ = self.audit(f"{length}-letter held-out assessment (repeat; never auto-trained)", rows, show_answers=False)
            scores[length] = score
        self.bridge["audit_history"].append({"cycle": self.bridge["cycle"], "updates": self.core.updates, "scores": scores})
        if scores.get("3", 0) >= 0.9:
            self.bridge["max_length"] = 4
        if self.stopping or not all(score >= 0.9 for score in scores.values()):
            return False
        # A separate unused exam confirms the repeated validation result.
        fresh = reserved_bank(self.config.seed + self.bridge["cycle"] * 7919 + 900001,
                              self.seen | self.reserved_keys)
        protected = []
        for length, stored in fresh.items():
            rows = [LanguageExample(**q) for q in stored]
            self.seen.update(q.key for q in rows)
            score, good = self.audit(f"{length}-letter fresh confirmation", rows, show_answers=True)
            protected.extend(good)
            if score < 0.9 or self.stopping:
                return False
        if not self.retained_skills_pass():
            return False
        self.school["passed"].append(STAGES[0].stage_id)
        self.school["retention"][STAGES[0].stage_id] = [asdict(q) for q in protected + [letters_case(c) for c in LETTERS]]
        self.school["stage_index"], self.school["round"] = 1, 0
        self.emit("lessons", "stage-passed", "English sequence checks passed at 90% or higher with earlier skills retained. Written word-formation lessons are now unlocked; meanings are not yet certified.")
        self.save("bridge-sequences-passed")
        return True

    def run_round(self, stage):
        if stage != STAGES[0] or self.school["letter_count"] < 52:
            super().run_round(stage)
            return
        witness = self.root / "before-bridge-round.pt"
        self.core.save(witness)
        self.candidate_active = True
        cycle = self.bridge["cycle"]
        lane = self.bridge_catalog["lanes"][cycle % len(self.bridge_catalog["lanes"])]
        state = self.bridge["lanes"][lane["id"]]
        characters = lane["characters"][:state["count"]]
        self.topic = f"Short sequences + {lane['language_goal']} writing foundation"
        accepted = False
        try:
            self.emit("lessons", "multilingual-lesson", f"{self.topic}\nScript: {lane['script']} | logical direction: {lane['direction']}\nCharacters: {' '.join(characters)}\n{lane['scope']}\nOriginal Unicode source; generated exact-copy exercises, not translated prose.",
                      source_id=self.bridge_catalog["source_id"], language_goal=lane["language_goal"], script=lane["script"])
            practice = sequence_practice(self.config.seed + cycle * 3571, self.reserved_keys,
                                         max_length=self.bridge["max_length"])
            word_rows = [letters_case(w) for w in self.bridge_catalog["english_copy_words"]]
            word_rows = [q for q in word_rows if q.key not in self.reserved_keys]
            foreign = [letters_case(c) for c in characters]
            # Rehearsal is deliberately smaller than the new sequence lesson.
            # One shared model sees interleaved examples; language lanes are serial.
            operations = mixed_questions(self.config.seed + cycle * 2971,
                                         difficulty=self.bridge["quiz_difficulty"],
                                         extra_characters=characters,
                                         exclude=self.reserved_keys,
                                         avoid_sequences=self.reserved_sequences)
            feedback = [LanguageExample(**q) for q in self.bridge["pending_feedback"]]
            rehearsal = self.script_rehearsal()
            mixed = practice + operations + feedback + word_rows * 2 + foreign * 3 + rehearsal * 2 + [letters_case(c) for c in LETTERS]
            self.teach_examples(mixed, epochs=4)
            if self.stopping:
                return
            self.audit("Short word copying: familiar practice, not meaning", word_rows, show_answers=True)
            self.audit("Sequence practice check: familiar, not a held-out pass", practice[:16], show_answers=True)
            score, good = self.audit(f"{lane['language_goal']}: familiar written characters, not comprehension", foreign, show_answers=True)
            retained, _ = self.audit("52 earlier Latin letters: retention only", [letters_case(c) for c in LETTERS])
            if retained < 1 and not self.stopping:
                self.teach_examples([letters_case(c) for c in LETTERS] + rehearsal * 2 + foreign, epochs=2)
                retained, _ = self.audit("52 earlier Latin letters: retention recheck", [letters_case(c) for c in LETTERS])
                # Re-evaluate new results after any remedial update.
                score, good = self.audit(f"{lane['language_goal']}: post-rehearsal familiar characters", foreign)
            retained_ok = retained == 1 and self.retained_skills_pass() and not self.stopping
            if not retained_ok and not self.stopping:
                self.emit("lessons", "cross-script-rehearsal", "Revisit previously learned characters across every active script before accepting this update.")
                self.teach_examples([letters_case(c) for c in LETTERS] + rehearsal * 2 + foreign * 2, epochs=2)
                retained_ok = self.retained_skills_pass() and not self.stopping
                score, good = self.audit(f"{lane['language_goal']}: after cross-script rehearsal", foreign)
            accepted = retained_ok and not self.stopping
            if accepted:
                state["correct_characters"] = sorted(set(state["correct_characters"]) | {q.answer for q in good})
                state["history"].append({"cycle": cycle, "score": score, "taught_count": len(characters)})
                if score >= 0.9:
                    state["count"] = min(len(lane["characters"]), state["count"] + 4)
            else:
                self.emit("learning", "bridge-rollback", "The candidate regressed a protected skill or was interrupted; restore the previous configuration.")
        finally:
            if not accepted:
                self.core = WaveLearner.load(witness)
            self.candidate_active = False
        self.bridge["cycle"] += 1
        self.school["round"] += 1
        self.emit("learning", "bridge-cycle", f"Bridge cycle {cycle}: {'accepted' if accepted else 'rolled back'}; model size unchanged.",
                  accepted=accepted, ledger=self.core.ledger())
        if not self.stopping:
            self.mixed_quiz(characters)
        if not self.stopping and cycle % 5 == 0:
            self.assessment()
        if time.monotonic() - self.last_save >= 180:
            self.save("bridge-periodic-accepted")
