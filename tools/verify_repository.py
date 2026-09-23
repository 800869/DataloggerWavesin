"""Audita archivos versionables y el índice sin imprimir valores sensibles.

No modifica archivos, no prepara commits y no accede a la BeagleBone.
La detección de secretos es heurística, no una garantía universal.
"""
import ast
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
PRIVATE_PREFIXES = ("data/", "logs/", "docs/private/", "backups/")
PRIVATE_SUFFIX = re.compile(
    r"(?:\.sqlite[^/]*|\.db(?:-\w+)?|\.py[co]|\.tar(?:\..*)?|"
    r"\.zip|\.jar|\.class|\.log(?:\..*)?|\.pem|\.key|\.pfx)$", re.I
)
CONTENT_RULES = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "private-ip": re.compile(
        r"\b(?:192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|"
        r"172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b"
    ),
    "personal-windows-path": re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\s]+", re.I),
    "assigned-secret": re.compile(
        r'''(?im)^\s*["']?(?:password|passwd|ftpPassword|api_key|access_token|secret)'''
        r'''["']?\s*[:=]\s*["']?[A-Za-z0-9+/_.-]{8,}'''
    ),
    "github-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
}


def git(*args, input=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, input=input)


def inspect_content(name, raw, source, errors):
    if b"\x00" in raw:
        errors.append(f"{source}: binary file requires review: {name}")
        return
    text = raw.decode("utf-8-sig")
    for label, pattern in CONTENT_RULES.items():
        if pattern.search(text):
            errors.append(f"{source}: {label}: {name}")
    if name.endswith(".py"):
        tree = ast.parse(text, filename=name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules = [node.module]
            else:
                continue
            for module in modules:
                if module and importlib.util.find_spec(module) is None:
                    errors.append(f"{source}: unresolved import {module}: {name}")


def main():
    errors = []
    names = sorted(set(
        name.decode("utf-8") for name in
        git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if name
    ))
    staged = {
        name.decode("utf-8") for name in git("ls-files", "-z").split(b"\0") if name
    }
    for name in names:
        if (name.startswith(PRIVATE_PREFIXES) or PRIVATE_SUFFIX.search(name)
                or "__pycache__/" in name or name == ".env"):
            errors.append(f"Private/generated path included by Git: {name}")
            continue
        path = ROOT / name
        if not path.is_file():
            errors.append(f"Missing file: {name}")
            continue
        inspect_content(name, path.read_bytes(), "worktree", errors)
        if name in staged:
            inspect_content(name, git("show", f":{name}"), "index", errors)

    probes = [
        "data/database/historicos.sqlite", "data/raw/example.txt",
        "data/raw/extraido/etc/shadow", "data/processed/resumen_historicos.json",
        "logs/run.log", "docs/private/example.md", ".env", "config/auth.local.json",
        "src/dataloggerwavesin/__pycache__/sample.pyc", ".venv/example",
        "backup.tar", "backup.zip", "sample.sqlite-wal", "sample.db-shm",
    ]
    ignored = git("check-ignore", "--no-index", "--stdin", input=("\n".join(probes)+"\n").encode())
    ignored_set = set(ignored.decode().splitlines())
    for name in probes:
        if name not in ignored_set:
            errors.append(f"Missing ignore rule: {name}")
    if errors:
        print("\n".join(sorted(set(errors))))
        return 1
    print(f"OK: {len(names)} versionable files; {len(staged)} index entries; "
          f"{len(probes)} ignore rules; Python syntax/imports and heuristic secret scan.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
