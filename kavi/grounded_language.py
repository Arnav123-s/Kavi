"""Example-induced sentence frames and explicit source-linked lexical memory.

No external predictor is used. Annotation supplies the target interpretation;
learned frames generalize slot contents, not arbitrary language or world truth.
"""

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import re
import unicodedata


def tokens(text):
    if not isinstance(text, str) or len(text) > 4096:
        raise ValueError("Use at most 4096 text characters.")
    return re.findall(r"\d+|[\u3400-\u9fff]|[^\W\d_\u3400-\u9fff]+|[^\w\s]",
                      unicodedata.normalize("NFC", text.casefold()), re.UNICODE)


def normalized(text):
    words = tokens(text)
    while words and words[-1] in {".", "?", "!"}:
        words.pop()
    return words


class LanguageModel:
    def __init__(self):
        self.rules = []
        self.lexicon = {}
        self.evidence = []
        self.definitions = {}
        self.training_stats = {"examples": 0, "alignments": 0}

    def teach(self, lessons, check=lambda: None, notify=lambda _: None):
        """Infer typed slot templates by alignment against supplied meanings."""
        groups = {}
        for lesson in lessons:
            check()
            self.training_stats["examples"] += 1
            words, target = normalized(lesson["text"]), lesson["target"]
            numeric = target["kind"] == "calculation"
            slots = {f"n{i}": value for i, value in enumerate(target["inputs"])} if numeric else target["slots"]
            assignments = []
            for name, value in slots.items():
                span = [str(value)] if numeric else normalized(value)
                positions = [i for i in range(len(words)-len(span)+1) if words[i:i+len(span)] == span]
                if not positions:
                    raise ValueError("A teaching slot is absent from its sentence.")
                assignments.append([(name, i, len(span)) for i in positions])
            candidates = []
            for assignment in itertools.product(*assignments):
                check()
                self.training_stats["alignments"] += 1
                if self.training_stats["alignments"] > 100000:
                    raise ValueError("Teaching alignment budget exceeded.")
                occupied = [i for _, start, length in assignment for i in range(start, start+length)]
                if len(occupied) != len(set(occupied)):
                    continue
                starts = {start: (name, length) for name, start, length in assignment}
                pattern, index = [], 0
                while index < len(words):
                    if index in starts:
                        name, length = starts[index]
                        pattern.append({"slot": name, "type": "natural" if numeric else "text"})
                        index += length
                    else:
                        pattern.append(words[index])
                        index += 1
                rule = {"pattern": pattern, "kind": target["kind"], "label": target["label"]}
                key = json.dumps(rule, sort_keys=True)
                groups.setdefault(key, {"rule": rule, "examples": set(), "sources": set()})
                groups[key]["examples"].add(lesson["text"])
                groups[key]["sources"].add(lesson["source"])
                candidates.append(key)
            if not candidates:
                raise ValueError("No nonoverlapping teaching alignment.")
        for value in groups.values():
            if len(value["examples"]) >= 2:
                rule = {**value["rule"], "support": len(value["examples"]), "sources": sorted(value["sources"])}
                if rule not in self.rules:
                    self.rules.append(rule)
                    notify(rule)
        if len(self.rules) > 256:
            raise ValueError("Sentence-rule budget exceeded.")

    def read_passage(self, text, source):
        """Retain word adjacency as lexical exposure, not interpreted knowledge."""
        words = [w for w in tokens(text) if w.isalpha()]
        counts = Counter(words)
        for word, count in counts.items():
            entry = self.lexicon.setdefault(word, {"count": 0, "next": {}, "sources": []})
            entry["count"] += count
            if source not in entry["sources"]:
                entry["sources"].append(source)
        for left, right in zip(words, words[1:]):
            following = self.lexicon[left]["next"]
            following[right] = following.get(right, 0) + 1
        if len(self.lexicon) > 20000:
            raise ValueError("Lexical node budget exceeded.")
        self.evidence.append({"source": source, "sha256": hashlib.sha256(text.encode()).hexdigest(),
                              "tokens": len(words)})

    def interpret(self, text, check=lambda: None):
        words = normalized(text)
        if len(words) > 96:
            return {"state": "unsupported", "reason": "Sentence exceeds 96 tokens."}
        meanings = {}
        for rule in self.rules:
            check()
            states = [(0, {})]
            for item in rule["pattern"]:
                next_states = []
                for position, bound in states:
                    check()
                    if isinstance(item, str):
                        if position < len(words) and words[position] == item:
                            next_states.append((position+1, bound))
                    elif item["type"] == "natural":
                        if position < len(words) and words[position].isascii() and words[position].isdigit():
                            next_states.append((position+1, {**bound, item["slot"]: int(words[position])}))
                    else:
                        for end in range(position+1, len(words)+1):
                            next_states.append((end, {**bound, item["slot"]: " ".join(words[position:end])}))
                            if len(next_states) > 10000:
                                return {"state": "unsupported", "reason": "Parsing budget exceeded."}
                states = next_states
                if len(states) > 10000:
                    return {"state": "unsupported", "reason": "Parsing budget exceeded."}
            for position, bound in states:
                if position != len(words):
                    continue
                meaning = {"kind": rule["kind"], "label": rule["label"]}
                if rule["kind"] == "calculation":
                    meaning["inputs"] = [bound[f"n{i}"] for i in range(len(bound))]
                else:
                    meaning["slots"] = bound
                meanings[json.dumps(meaning, sort_keys=True)] = meaning
        if len(meanings) != 1:
            return {"state": "ambiguous" if meanings else "unsupported", "alternatives": len(meanings)}
        return {"state": "interpreted", "meaning": next(iter(meanings.values()))}

    def answer(self, text, library, check=lambda: None):
        parsed = self.interpret(text, check=check)
        if parsed["state"] != "interpreted":
            return parsed
        meaning = parsed["meaning"]
        if meaning["kind"] == "lookup":
            term = meaning["slots"]["term"]
            entries = self.definitions.get(term, [])
            if len(entries) != 1:
                return {**parsed, "state": "ambiguous" if entries else "unsupported", "senses": len(entries)}
            return {**parsed, "definition": entries[0], "status": "source-linked lexical recall"}
        if meaning["kind"] == "calculation":
            try:
                result = library.execute(meaning["label"], tuple(meaning["inputs"]), trace=True, check=check)
                return {**parsed, "value": result.value, "calls": result.calls, "iterations": result.iterations,
                        "trace": result.trace, "trace_events": result.trace_events,
                        "trace_truncated": result.trace_truncated}
            except ValueError as error:
                return {**parsed, "state": "execution_failed", "reason": str(error)}
        return {**parsed, "status": "sentence relation identified; truth and argument validity unassessed"}

    def encoded(self):
        return (json.dumps({"schema": "kavi.grounded-language.v1", "rules": self.rules,
                            "lexicon": self.lexicon, "evidence": self.evidence, "definitions": self.definitions},
                           sort_keys=True, separators=(",", ":")) + "\n").encode()

    @classmethod
    def load(cls, path):
        path = Path(path)
        if path.stat().st_size > 4_000_000:
            raise ValueError("Language model exceeds four MB.")
        value = json.loads(path.read_text(encoding="utf-8"))
        if set(value) != {"schema", "rules", "lexicon", "evidence", "definitions"} or value["schema"] != "kavi.grounded-language.v1":
            raise ValueError("Invalid language schema.")
        if not isinstance(value["rules"], list) or len(value["rules"]) > 256:
            raise ValueError("Invalid sentence rules.")
        if not isinstance(value["lexicon"], dict) or len(value["lexicon"]) > 20000 or not isinstance(value["definitions"], dict):
            raise ValueError("Invalid lexical memory.")
        for rule in value["rules"]:
            if (not isinstance(rule, dict) or set(rule) != {"pattern", "kind", "label", "support", "sources"}
                    or rule["kind"] not in {"calculation", "relation", "lookup"}
                    or not isinstance(rule["label"], str) or not isinstance(rule["pattern"], list)
                    or not 1 <= len(rule["pattern"]) <= 96):
                raise ValueError("Malformed sentence rule.")
            slots = []
            slot_types = []
            for item in rule["pattern"]:
                if isinstance(item, str):
                    continue
                if (not isinstance(item, dict) or set(item) != {"slot", "type"}
                        or item["type"] not in {"natural", "text"} or not isinstance(item["slot"], str)):
                    raise ValueError("Malformed sentence slot.")
                slots.append(item["slot"])
                slot_types.append(item["type"])
            if not slots or len(slots) > 3 or len(slots) != len(set(slots)):
                raise ValueError("Invalid sentence-slot count.")
            if rule["kind"] == "calculation" and set(slots) != {f"n{i}" for i in range(len(slots))}:
                raise ValueError("Invalid arithmetic slot bindings.")
            if any(t != ("natural" if rule["kind"] == "calculation" else "text") for t in slot_types):
                raise ValueError("Slot types disagree with the meaning kind.")
            if rule["kind"] == "lookup" and slots != ["term"]:
                raise ValueError("Invalid lexical lookup binding.")
        for term, entries in value["definitions"].items():
            if not isinstance(entries, list) or any(
                not isinstance(entry, dict) or set(entry) != {"term", "meaning", "source", "kind"}
                or entry["term"] != term or not all(isinstance(v, str) for v in entry.values())
                for entry in entries
            ):
                raise ValueError("Invalid lexical entry.")
        result = cls()
        result.rules, result.lexicon, result.evidence = value["rules"], value["lexicon"], value["evidence"]
        result.definitions = value["definitions"]
        return result
