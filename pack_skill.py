#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 homework-solver/ 打成 .skill 包（zip 格式），同名覆盖。

跑法：  python pack_skill.py
产出：  ../卢怡然_C4C_homework-solver.skill
副产物：../evidence/skill_manifest.json（包内每个文件的 sha256，用于自足核对）
"""
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent      # C4C/（本脚本就放在这里）
SRC = ROOT / "homework-solver"
OUT = ROOT / "卢怡然_C4C_homework-solver.skill"
MANIFEST = ROOT / "evidence" / "skill_manifest.json"

SKIP_DIRS = {"__pycache__", ".git", ".ipynb_checkpoints"}
SKIP_FILES = {".DS_Store"}


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main():
    if not SRC.is_dir():
        print(f"找不到源目录 {SRC}")
        sys.exit(1)

    files = []
    for p in sorted(SRC.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(SRC)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name in SKIP_FILES:
            continue
        files.append((rel.as_posix(), p))

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    entries = {}
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, p in files:
            data = p.read_bytes()
            arcname = f"homework-solver/{rel}"
            z.writestr(arcname, data)
            entries[arcname] = {"sha256": sha256_bytes(data), "size": len(data)}

    MANIFEST.write_text(json.dumps({
        "skill": OUT.name,
        "skill_sha256": sha256_bytes(OUT.read_bytes()),
        "skill_size": OUT.stat().st_size,
        "file_count": len(entries),
        "files": entries,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"打包 {len(entries)} 个文件 → {OUT.name}")
    print(f"字节 {OUT.stat().st_size:,}  sha256 {entries and sha256_bytes(OUT.read_bytes())[:16]}…")

    # 自足核对：解回来逐个重算 sha256，不能只相信"打包没报错"
    bad = 0
    with zipfile.ZipFile(OUT) as z:
        for arcname, meta in entries.items():
            if sha256_bytes(z.read(arcname)) != meta["sha256"]:
                print(f"  × 包内不一致: {arcname}")
                bad += 1
    print("包内 sha256 全部一致" if not bad else f"有 {bad} 个文件不一致")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
