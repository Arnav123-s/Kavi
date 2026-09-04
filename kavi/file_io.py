"""Small atomic file operations tolerant of transient Windows reader locks."""

from pathlib import Path
import time


def atomic_replace(temporary: Path, destination: Path, *, attempts: int = 50) -> None:
    """Keep the old valid file visible until replacement succeeds.

    Windows may reject a rename while a reader briefly has the destination
    open without delete sharing. Retry those access/sharing errors only;
    persistent errors remain visible instead of silently losing checkpoints.
    """
    if not 1 <= attempts <= 100:
        raise ValueError("Invalid replacement retry budget.")
    for attempt in range(attempts):
        try:
            temporary.replace(destination)
            return
        except OSError as error:
            transient = isinstance(error, PermissionError) or getattr(error, "winerror", None) in (5, 32, 33)
            if not transient or attempt == attempts - 1:
                raise
            time.sleep(min(0.01 * (attempt + 1), 0.05))
