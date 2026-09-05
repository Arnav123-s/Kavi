# Operations and reproducibility

Author: [Arnav123-s](https://github.com/Arnav123-s)

Run commands from the repository root. The project declares Python 3.11 or later. The verified environment is Python 3.13.5 with PyTorch 2.6.0+cu124. The symbolic modules use the standard library; the text model and its tests require PyTorch.

## Environment and inspection

Use a dedicated environment when setting up another machine. The optional dependency group is declared in `pyproject.toml`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e '.[wave]'
```

Installation downloads dependencies. To inspect an existing environment and run the regression suite:

```powershell
python --version
python -B -m unittest discover -s tests -q
python -m kavi --help
python -m kavi.source_cli
python -m kavi.school_cli --list
python -m kavi.pathway_cli --help
python -m kavi.wave_cli --help
```

The source command reads admission metadata; it does not fetch books. Tests include small bounded learning checks. All 138 tests passed after relocation on 5 September 2026.

## Text learning

`kavi.wave_cli run` starts a teacher and modifies learner state. It requires a run directory under `runs` and a foundation checkpoint. Source files must match the admitted private fingerprints. `--resume` selects a prior text run; `--multilingual-bridge` selects the small additional writing-system curriculum.

Inspect the full argument list before preparing a finite run:

```powershell
python -m kavi.wave_cli run --help
```

The launcher `scripts/start-live-learning.ps1` creates Windows Terminal tabs for the teacher, feeds and controls. Its defaults are 12 rounds and 86,400 seconds, with a historical local foundation path. Set explicit budgets and a valid foundation for each reviewed run.

The launcher includes `--keep-available`, which keeps the interactive service available after curriculum work. A teaching budget and process lifetime are separate controls. Closing a feed or console does not stop the teacher.

For an existing selected run, replace `runs\selected-run` with its actual directory:

```powershell
python -m kavi.wave_cli watch --run-dir 'runs\selected-run' --channel answers
python -m kavi.wave_cli console --run-dir 'runs\selected-run'
```

`watch` reads recorded feeds. The console accepts `/status`, `/pause`, `/resume`, `/stop` and `/quit`; `/quit` closes only the console. Ordinary questions and `/teach question => answer || explanation` enqueue learner interaction. Teaching changes the selected learner when its process consumes the queue.

## Symbolic experiments

The initial arithmetic experiment exposes routes with:

```powershell
python -m kavi paths
```

A finite teaching example, to use within an approved experiment, is:

```powershell
python -u -m kavi live --steps 24 --seed 7 --ask 7 5 add
```

The explanation experiment uses `python -m kavi.lesson_cli`. The unified symbolic curriculum uses `python -m kavi.pathway_cli`; `scripts/start-live-pathways.ps1` opens its live views. These are different cores from the recurrent text model.

The original stage-0 control files are explicit arguments:

```powershell
python -u -m kavi live --steps 100 --pause-file '.\PAUSE' --stop-file '.\STOP'
```

Creating `PAUSE` pauses at a control check; removing that file resumes. Creating `STOP` ends at the next check. Stage 0 does not persist a trained checkpoint on stop. Later runtimes have their own checkpoint and control mechanisms.

## Sources and relocation

The local checkout is now at `C:\Users\admin\Desktop\PI&E`. Launchers derive the root from their script location. Run them from the checkout so Python resolves the package and relative resources correctly.

Private sources, run directories and checkpoints moved with the repository. Historical logs retain their original paths. A bare public clone does not include those private inputs, so a source-dependent run cannot be reproduced from public code alone.

The [source gate](DOCUMENT_CURRICULUM_GATE.md) specifies admission requirements. Check source identifiers, exact file hashes and reviewed scope before using a source.

## Resource accounting

Record model parameters, optimizer state, replay, checkpoints, search workspace and source storage separately. Parameter size is not process memory. Process CPU time and wall time also differ, especially with multiple threads.

Current text experiments execute on CPU. Installed CUDA support does not establish GPU use. Temperature readings are unavailable unless a working sensor supplies them. Maintain finite time, step, candidate and disk limits, plus pause and stop controls.

## Experiment record

Preserve code revision and diff, dependency versions, hardware, thread count, seeds, source hashes, starting model hash, task generators, budgets, selection criteria, per-case outputs, resource observations and stopping reason. Record failed candidates and regressions.

Use the [evaluation protocol](EVALUATION_PROTOCOL.md) and [experiment record format](../experiments/README.md). Real curriculum restarts and hardware-policy changes require a reviewed configuration and project authorization.
