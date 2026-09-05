"""Conservative local resource readings; no guessed CPU temperature."""

import os
import sys


def memory_reading():
    if sys.platform != "win32":
        return {"available_bytes": None, "working_set_bytes": None, "peak_bytes": None}
    import ctypes
    from ctypes import wintypes

    class Memory(ctypes.Structure):
        _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
            (key, ctypes.c_ulonglong) for key in ("total", "available", "page_total", "page_available",
                                                 "virtual_total", "virtual_available", "extended")]

    class Process(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("faults", wintypes.DWORD)] + [
            (key, ctypes.c_size_t) for key in ("peak", "working", "quota_peak", "quota", "nonpaged_peak",
                                             "nonpaged", "pagefile", "peak_pagefile")]

    kernel, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    host, process = Memory(), Process()
    host.length = ctypes.sizeof(host)
    available = host.available if kernel.GlobalMemoryStatusEx(ctypes.byref(host)) else None
    ok = psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(process), ctypes.sizeof(process))
    return {"available_bytes": available, "working_set_bytes": process.working if ok else None,
            "peak_bytes": process.peak if ok else None, "logical_cpus": os.cpu_count(),
            "cpu_temperature": None, "temperature_note": "No reliable CPU-temperature telemetry is available here."}


def parallel_rows(reading):
    available, working = reading.get("available_bytes"), reading.get("working_set_bytes")
    if available is None or working is None:
        return 1
    if available >= 6 * 1024 ** 3 and working < 640 * 1024 ** 2:
        return 4
    if available >= 4 * 1024 ** 3 and working < 768 * 1024 ** 2:
        return 2
    return 1
