#!/usr/bin/env python3
"""Read bounded storage/runtime counters without installing or starting a service.

Usage: python probe_picker_host.py --path TASK_DIRECTORY [--measure PUBLIC_ASSETS]
See docs/ppt-project/DOTS_PICKER_HOST_ASSESSMENT.md. This cannot identify a Dot
computer from an operator label or certify service persistence or account quota.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from console_encoding import configure_utf8_stdio


def _counter(path: str) -> str | None:
    file = Path(path)
    if not file.is_file():
        return None
    try:
        return file.read_text(encoding="ascii").strip()[:200]
    except (OSError, UnicodeError):
        return None


def _version(command: str) -> dict:
    executable = shutil.which(command)
    if executable is None:
        return {"present": False}
    try:
        result = subprocess.run([executable, "--version"], capture_output=True,
                                text=True, timeout=5, errors="replace")
        return {"present": True, "exit": result.returncode,
                "version": (result.stdout or result.stderr).strip()[:200]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"present": True, "version_verified": False, "reason": type(exc).__name__}


def _footprint(path: Path) -> dict:
    if not path.is_dir():
        raise ValueError("--measure must name an existing directory")
    def fail(error):
        raise error

    total, count = 0, 0
    for current, directories, files in os.walk(path, followlinks=False, onerror=fail):
        directories[:] = [name for name in directories
                          if name not in {".git", "node_modules", "__pycache__"}
                          and not (Path(current) / name).is_symlink()]
        for name in files:
            file = Path(current) / name
            if file.is_symlink():
                continue
            total += file.stat().st_size
            count += 1
            if count >= 20000:
                return {"bytes": total, "files": count, "complete": False}
    return {"bytes": total, "files": count, "complete": True,
            "excludes": [".git", "node_modules", "__pycache__", "symlinks"]}


def main() -> int:
    configure_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, required=True)
    parser.add_argument("--measure", type=Path, action="append", default=[])
    args = parser.parse_args()
    path = args.path.resolve(strict=True)
    if not path.is_dir():
        parser.error("--path must be an existing task directory")
    disk = shutil.disk_usage(path)
    memory_max = _counter("/sys/fs/cgroup/memory.max")
    memory_current = _counter("/sys/fs/cgroup/memory.current")
    cpu = _counter("/sys/fs/cgroup/cpu.max")
    report = {
        "schema_version": 1,
        "platform": platform.system(), "architecture": platform.machine(),
        "python_version": platform.python_version(), "node": _version("node"),
        "logical_cpu_count": os.cpu_count(),
        "cgroup_v2": {"memory_max": memory_max, "memory_current": memory_current, "cpu_max": cpu},
        "filesystem_view": {"total_bytes": disk.total, "used_bytes": disk.used, "free_bytes": disk.free},
        "measured_directories": [_footprint(item.resolve(strict=True)) for item in args.measure],
        "identity_bound_to_dot_computer": False,
        "account_storage_quota_verified": False,
        "persistent_server_support_verified": False,
        "outbound_tunnel_access_verified": False,
        "limitations": ["Filesystem view is not proof of the account quota",
                        "Host counters may differ from container or plan limits",
                        "Retained disk state is not proof of a continuously running process",
                        "Correlate this receipt with the actual selected platform computer"],
        "mutations": [], "network_requests": 0,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
