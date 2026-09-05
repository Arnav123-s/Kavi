"""Visible controls and a persistent transcript for bounded learning runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk


class LearningWindow:
    def __init__(self, root: tk.Tk, run_dir: Path, config: Path,
                 preparation: Path, ready_file: Path):
        self.root, self.run_dir, self.config = root, run_dir.resolve(), config.resolve()
        self.preparation, self.ready_file = preparation, ready_file
        self.process = None
        self.messages = queue.Queue()
        self.last_preparation = None
        self.last_status = None
        self.library_digest = None
        root.title("Kavi Live Learning")
        root.geometry("1180x760")
        root.minsize(820, 520)
        root.configure(bg="#15191f")
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TFrame", background="#15191f")
        style.configure("TLabel", background="#15191f", foreground="#e7edf4")
        style.configure("TButton", padding=8)
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"))
        top = ttk.Frame(root, padding=16)
        top.pack(fill="x")
        ttk.Label(top, text="Kavi | Live Learning", style="Title.TLabel").pack(anchor="w")
        self.headline = tk.StringVar(value="PREPARING — no learning has started")
        ttk.Label(top, textvariable=self.headline, font=("Segoe UI", 11)).pack(anchor="w", pady=(7, 3))
        ttk.Label(top, text="Finite experiments · actual events · saved procedures · independent final tests").pack(anchor="w")
        actions = ttk.Frame(root, padding=(16, 0, 16, 10))
        actions.pack(fill="x")
        self.start_button = ttk.Button(actions, text="Start teaching", command=self.start, state="disabled")
        self.start_button.pack(side="left", padx=(0, 7))
        for label, action in (("Pause", "pause"), ("Resume", "resume"), ("Stop", "stop")):
            ttk.Button(actions, text=label, command=lambda a=action: self.control(a)).pack(side="left", padx=4)
        self.summary = tk.StringVar(value="Waiting for the reviewed configuration and implementation checks.")
        ttk.Label(root, textvariable=self.summary, padding=(16, 0, 16, 10), wraplength=1120).pack(anchor="w")
        panel = ttk.Frame(root, padding=(16, 0, 16, 8))
        panel.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(panel)
        scrollbar.pack(side="right", fill="y")
        self.transcript = tk.Text(panel, bg="#0b0f14", fg="#dce7ee", insertbackground="white",
                                  font=("Consolas", 11), relief="flat", wrap="word",
                                  yscrollcommand=scrollbar.set, state="disabled")
        self.transcript.pack(fill="both", expand=True)
        scrollbar.configure(command=self.transcript.yview)
        query = ttk.Frame(root, padding=(16, 4, 16, 10))
        query.pack(fill="x")
        ttk.Label(query, text="Query a saved procedure:").pack(side="left", padx=(0, 8))
        self.operation = ttk.Combobox(query, width=24, state="readonly")
        self.operation.pack(side="left", padx=(0, 8))
        self.operands = ttk.Entry(query, width=32)
        self.operands.insert(0, "12 5")
        self.operands.pack(side="left", padx=(0, 8))
        ttk.Button(query, text="Execute and trace", command=self.ask).pack(side="left")
        self.operands.bind("<Return>", lambda _: self.ask())
        ttk.Label(root, text="Closing this window requests a stop. Completed evidence remains on disk.",
                  padding=(16, 0, 16, 12)).pack(anchor="w")
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.append("This window shows the actual learning process when it starts.\n"
                    "Preparation is in progress; the Start button becomes available after implementation checks.\n"
                    "There is no current claim of university or master's-level competence.\n")
        root.after(250, self.poll)

    def append(self, text: str):
        self.transcript.configure(state="normal")
        self.transcript.insert("end", text)
        if int(self.transcript.index("end-1c").split(".")[0]) > 2400:
            self.transcript.delete("1.0", "401.0")
        self.transcript.configure(state="disabled")
        self.transcript.see("end")

    def start(self):
        if self.process is not None or (self.ready_file is not None and not self.ready_file.exists()):
            return
        if self.run_dir.exists():
            self.append("Cannot start: choose a new run directory. Existing evidence is preserved.\n")
            return
        command = [sys.executable, "-B", "-u", "-m", "kavi.library_cli", "run",
                   "--config", str(self.config), "--run-dir", str(self.run_dir)]
        try:
            self.process = subprocess.Popen(command, cwd=Path(__file__).resolve().parents[1],
                                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                             text=True, encoding="utf-8", errors="replace",
                                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except OSError as error:
            self.append(f"Could not launch the learner: {error}\n")
            return
        self.start_button.configure(state="disabled")
        self.headline.set("RUNNING — finite source-guided operation curriculum")
        self.append("\n=== LIVE RUN STARTED ===\n")

        def collect():
            for line in self.process.stdout:
                self.messages.put(line)
            self.messages.put(f"\nLearner process exited with code {self.process.wait()}.\n")
        threading.Thread(target=collect, daemon=True).start()

    def control(self, action):
        if not self.run_dir.exists() or self.process is None or self.process.poll() is not None:
            return
        if action == "resume":
            (self.run_dir / "PAUSE").unlink(missing_ok=True)
        else:
            (self.run_dir / ("PAUSE" if action == "pause" else "STOP")).touch()
        self.append(f"Control requested: {action}\n")

    def ask(self):
        try:
            from .procedure_core import ProcedureLibrary
            library = ProcedureLibrary.load(self.run_dir / "library.json")
            name = self.operation.get()
            args = tuple(int(part) for part in self.operands.get().replace(",", " ").split())
            result = library.execute(name, args, trace=True)
            self.append(f"\nQUERY {name}{args} = {result.value}\n"
                        f"  calls={result.calls}; frames={result.frames}; gate evaluations={result.gates}\n")
            for row in result.trace:
                self.append("  " + json.dumps(row, ensure_ascii=False) + "\n")
        except (OSError, ValueError, RuntimeError, ImportError) as error:
            self.append(f"Query unavailable: {error}\n")

    def poll(self):
        for _ in range(500):
            try:
                self.append(self.messages.get_nowait())
            except queue.Empty:
                break
        try:
            if self.process is None:
                raw = (self.preparation.read_text(encoding="utf-8") if self.preparation is not None
                       else json.dumps({"message": "Inspect the configuration, then start the finite teaching run."}))
                if raw != self.last_preparation:
                    self.last_preparation = raw
                    value = json.loads(raw)
                    self.summary.set(value["message"])
                    self.append("\nPREPARATION: " + value["message"] + "\n")
                if (self.ready_file is None or self.ready_file.exists()) and self.config.exists():
                    if str(self.start_button["state"]) == "disabled":
                        self.headline.set("READY — visible window established; start the reviewed trial here")
                        self.append("\nREVIEWED CONFIGURATION\n" + self.config.read_text(encoding="utf-8") + "\n")
                        self.start_button.configure(state="normal")
            elif (self.run_dir / "status.json").exists():
                status = json.loads((self.run_dir / "status.json").read_text(encoding="utf-8"))
                self.headline.set(f"{status['state'].upper()} | {status.get('phase', '')} | seed {status.get('seed', '-')}")
                self.summary.set(status.get("summary", "See the live transcript for candidate changes and evaluation."))
            model = self.run_dir / "library.json"
            if model.exists():
                raw = model.read_text(encoding="utf-8")
                if raw != self.library_digest:
                    self.library_digest = raw
                    entries = json.loads(raw)["procedures"]
                    self.operation["values"] = [entry["name"] for entry in entries]
                    if not self.operation.get() and entries:
                        self.operation.current(0)
        except (OSError, ValueError, KeyError):
            pass
        self.root.after(250, self.poll)

    def close(self):
        self.control("stop")
        self.root.destroy()


def main():
    parser = argparse.ArgumentParser(description="A visible, controlled window for Kavi learning.")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--preparation", type=Path)
    parser.add_argument("--ready-file", type=Path)
    args = parser.parse_args()
    root = tk.Tk()
    LearningWindow(root, args.run_dir, args.config, args.preparation, args.ready_file)
    root.mainloop()


if __name__ == "__main__":
    main()
