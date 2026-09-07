"""Plain-language progress and evidence for the configuration reuse trial."""

import json
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk


class GrowthView:
    def __init__(self, root, run_dir, config, start=False):
        self.root, self.run_dir, self.config = root, run_dir.resolve(), config.resolve()
        self.process, self.last = None, None
        root.title("Kavi | Learning reusable pathways")
        root.geometry("1100x780")
        root.configure(bg="#f4f6fa")
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Can one learned idea help Kavi learn the next?",
                  font=("Segoe UI", 20, "bold"), wraplength=1020).pack(anchor="w")
        ttk.Label(frame, text="Multiply a number by itself → repeat that learned idea → build a larger computation",
                  font=("Segoe UI", 11), wraplength=1020).pack(anchor="w", pady=(10, 16))
        self.status = tk.StringVar(value="Preparing a small, controlled experiment")
        ttk.Label(frame, textvariable=self.status, font=("Segoe UI", 13, "bold"),
                  wraplength=1020).pack(anchor="w", pady=8)
        self.explanation = tk.StringVar(value="Three learners get the same questions and search limits. Only what they retain differs.")
        ttk.Label(frame, textvariable=self.explanation, font=("Segoe UI", 11),
                  wraplength=1020).pack(anchor="w", pady=8)
        self.table = ttk.Treeview(frame, columns=("square", "fourth", "eighth", "storage"), height=3)
        self.table.heading("#0", text="What the learner keeps")
        self.table.column("#0", width=290)
        for key, label in (("square", "Square"), ("fourth", "Fourth power"),
                           ("eighth", "Eighth power"), ("storage", "Stored library")):
            self.table.heading(key, text=label)
            self.table.column(key, width=165, anchor="center")
        for arm, title in (("fixed", "Starting components only"), ("unrelated", "An unrelated doubling lesson"),
                           ("cumulative", "Earlier relevant configurations")):
            self.table.insert("", "end", iid=arm, text=title, values=("Waiting",)*4)
        self.table.pack(fill="x", pady=12)
        ttk.Label(frame, text="Unseen tests: correct completed answers out of 9. “Not acquired” means search found no candidate.",
                  wraplength=1020).pack(anchor="w")
        reading = ttk.Frame(frame)
        reading.pack(fill="both", expand=True, pady=14)
        scrollbar = ttk.Scrollbar(reading)
        scrollbar.pack(side="right", fill="y")
        self.text = tk.Text(reading, font=("Segoe UI", 11), wrap="word", height=14,
                            yscrollcommand=scrollbar.set,
                            bg="white", relief="flat", padx=14, pady=14)
        self.text.pack(fill="both", expand=True)
        scrollbar.configure(command=self.text.yview)
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        for label, action in (("Pause", "PAUSE"), ("Resume", "RESUME"), ("Stop", "STOP")):
            ttk.Button(controls, text=label, command=lambda a=action: self.control(a)).pack(side="left", padx=4)
        ttk.Label(controls, text="Completed results stay visible. Closing requests a stop during learning.").pack(side="left", padx=16)
        root.protocol("WM_DELETE_WINDOW", self.close)
        if start:
            root.after(1500, self.start)
        self.poll()

    def start(self):
        if self.run_dir.exists():
            return
        self.process = subprocess.Popen([sys.executable, "-B", "-m", "scripts.run_pathway_growth", "run",
            "--config", str(self.config), "--run-dir", str(self.run_dir)],
            cwd=Path(__file__).resolve().parents[1], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    def control(self, action):
        if not self.run_dir.exists():
            return
        if action == "RESUME":
            (self.run_dir / "PAUSE").unlink(missing_ok=True)
        else:
            (self.run_dir / action).touch()

    def poll(self):
        try:
            path = self.run_dir / "results.json"
            if path.exists():
                raw = path.read_text(encoding="utf-8")
                correction_path = self.run_dir / "correction.json"
                correction_raw = correction_path.read_text(encoding="utf-8") if correction_path.exists() else ""
                if raw + correction_raw != self.last:
                    self.last = raw + correction_raw
                    result = json.loads(raw)
                    self.status.set("Experiment " + result["state"] + " — these are measured results")
                    self.explanation.set("Compare acquired configurations and unseen answers below. These tests do not establish learning new laws or general understanding.")
                    lines = []
                    for arm, row in result["arms"].items():
                        values = [f"{x['held_out']['passed']} / {x['held_out']['total']}" if "held_out" in x
                                  else "Not acquired" for x in row["lessons"]]
                        if len(values) == 3:
                            self.table.item(arm, values=(*values, f"{row['final_bytes']} bytes"))
                        for lesson in row["lessons"]:
                            for case in lesson.get("held_out", {}).get("rows", []):
                                if not case["correct"]:
                                    reason = ("It reached the preset execution limit before finishing."
                                              if "budget exhausted" in case.get("error", "") else "The answer was incorrect or execution failed.")
                                    lines.append(f"Incomplete test: {lesson['name']} at input {case['inputs'][0]}. {reason}")
                    meanings = {"multiply(x0, x0)": "Multiply the input by itself.",
                                "square(square(x0))": "Apply the learned square operation twice.",
                                "fourth(square(x0))": "Combine learned square and fourth-power operations."}
                    cumulative = result["arms"].get("cumulative", {})
                    lines += ["", "Configurations acquired in the cumulative arm:"]
                    for lesson in cumulative.get("lessons", []):
                        lines.append(lesson["name"].capitalize() + ": " + meanings.get(lesson.get("description"),
                            "A candidate was acquired." if lesson.get("body") else "No candidate acquired."))
                    lines += ["", "Earlier-skill checks:"]
                    for arm, row in result["arms"].items():
                        checks = list(row.get("retention", {}).values())
                        lines.append(f"{arm.capitalize()}: {sum(x['passed'] for x in checks)} / {sum(x['total'] for x in checks)} completed correctly.")
                    if "final_bytes" in cumulative:
                        lines.append(f"\nCumulative library: {cumulative['initial_bytes']} → {cumulative['final_bytes']} bytes. Shared computations still require execution work.")
                    lines.append(f"The worker ran for {result['seconds']:.2f} seconds. Full evidence is saved; this screen is not a replay.")
                    if correction_raw:
                        correction = json.loads(correction_raw)
                        tests = correction["held_out"]
                        lines += ["", "SECOND EXPERIMENT: CAN A CORRECTION IMPROVE OTHER ANSWERS?",
                                  "The first lesson was too small: Kavi simply returned its input.",
                                  "For the square of 2, it answered 2. We taught it that the answer is 4.",
                                  "It then found the rule: multiply the input by itself.",
                                  f"On {len(tests)} fresh questions: {sum(x['before_correct'] for x in tests)} correct before, {sum(x['after_correct'] for x in tests)} after.",
                                  f"Original valid answers retained: {sum(correction['retention'])} / {len(correction['retention'])}.",
                                  "This shows correction of one reusable rule. It does not establish general understanding."]
                    self.text.delete("1.0", "end")
                    self.text.insert("end", "\n".join(lines))
            else:
                status = self.run_dir / "status.json"
                if status.exists():
                    value = json.loads(status.read_text(encoding="utf-8"))
                    names = {"fixed": "Testing the learner with starting components only",
                             "unrelated": "Testing whether an unrelated lesson helps",
                             "cumulative": "Testing reuse of relevant earlier lessons"}
                    self.status.set(names.get(value.get("phase"), "Evaluating unseen answers"))
                events = self.run_dir / "events.txt"
                if events.exists():
                    lessons = [x.split(":")[0].replace("TEACH ", "Learning ") for x in events.read_text(encoding="utf-8").splitlines() if x.startswith("TEACH ")]
                    self.text.delete("1.0", "end")
                    self.text.insert("end", "Current sequence:\n\n" + "\n".join(lessons) + "\n\nSearching possible configurations; test results appear after teaching finishes.")
        except (OSError, ValueError, KeyError):
            pass
        self.root.after(300, self.poll)

    def close(self):
        self.control("STOP")
        self.root.destroy()


def show(run_dir, config, start=False):
    root = tk.Tk()
    GrowthView(root, run_dir, config, start)
    root.mainloop()


if __name__ == "__main__":
    show(Path(sys.argv[1]), Path(sys.argv[2]))
