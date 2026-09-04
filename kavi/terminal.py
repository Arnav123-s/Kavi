"""Small terminal-output compatibility helpers for Kavi's CLIs."""

from __future__ import annotations

import sys


def configure_utf8_output() -> None:
    """Prefer UTF-8 so original-language metadata can be displayed faithfully.

    A legacy Windows console can otherwise reject Arabic, Chinese, Tamil, and
    other catalog characters before Kavi's own code receives a chance to show
    them. Failure to reconfigure is deliberately non-fatal for redirected or
    unusual streams; the caller still retains its normal Python output stream.
    """

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="backslashreplace")
        except (OSError, ValueError):
            continue
