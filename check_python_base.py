import os
import platform
import site
import shutil
import sys
from pathlib import Path


def _safe_site_packages():
    paths = []
    try:
        paths.extend(site.getsitepackages())
    except Exception:
        pass

    try:
        user_site = site.getusersitepackages()
        if user_site:
            paths.append(user_site)
    except Exception:
        pass

    # Preserve order, remove duplicates
    deduped = []
    seen = set()
    for p in paths:
        if p and p not in seen:
            seen.add(p)
            deduped.append(p)
    return deduped


def main():
    executable = Path(sys.executable).resolve()
    prefix = Path(sys.prefix).resolve()
    base_prefix = Path(getattr(sys, "base_prefix", sys.prefix)).resolve()
    real_prefix = getattr(sys, "real_prefix", "")

    in_venv = (str(prefix) != str(base_prefix)) or bool(real_prefix)

    print("=== Python Interpreter Resolution ===")
    print(f"Python version        : {sys.version.splitlines()[0]}")
    print(f"Platform              : {platform.platform()}")
    print(f"sys.executable        : {executable}")
    print(f"sys.prefix            : {prefix}")
    print(f"sys.base_prefix       : {base_prefix}")
    print(f"sys.real_prefix       : {real_prefix or '(not set)'}")
    print(f"Inside virtual env    : {in_venv}")

    print("\n=== Environment Variables ===")
    print(f"VIRTUAL_ENV           : {os.environ.get('VIRTUAL_ENV', '(not set)')}")
    print(f"CONDA_PREFIX          : {os.environ.get('CONDA_PREFIX', '(not set)')}")
    print(f"PYTHONHOME            : {os.environ.get('PYTHONHOME', '(not set)')}")
    print(f"PYTHONPATH            : {os.environ.get('PYTHONPATH', '(not set)')}")

    print("\n=== Command Discovery (from PATH) ===")
    print(f"python                : {shutil.which('python') or '(not found)'}")
    print(f"python3               : {shutil.which('python3') or '(not found)'}")
    print(f"py launcher           : {shutil.which('py') or '(not found)'}")
    print(f"pip                   : {shutil.which('pip') or '(not found)'}")

    print("\n=== Site-Packages ===")
    for p in _safe_site_packages():
        print(f"- {p}")

    print("\n=== sys.path (first 10 entries) ===")
    for i, p in enumerate(sys.path[:10], start=1):
        print(f"{i:2d}. {p}")


if __name__ == "__main__":
    main()
