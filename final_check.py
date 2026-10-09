# 提交前的最终核对清单
#
# 跑法：python final_check.py（在 C4C/ 下）
#
# 逐条核对「要提交到 GitHub 的东西」是否齐全、是否有空的、
# 哈希是否与包内留档一致。任何一条不过就退出码非 0。

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# CHALLENGE.md §必须提交的文件 —— 7 项，缺一项就无法评审
REQUIRED_DOCS = [
    "卢怡然_C4C_方案设计.md",
    "卢怡然_C4C_验证报告.md",
    "卢怡然_C4C_教学说明.md",
    "卢怡然_C4C_拿来说明.md",
    "卢怡然_C4C_AI日志.md",
    "卢怡然_C4C_作业原件.md",
    "卢怡然_C4C_output.pdf",
]

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((ok, name, detail))
    print(f"  [{'√' if ok else '×'}] {name}" + (f"  — {detail}" if detail else ""))
    return ok


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    print("=" * 64)
    print("C4C 提交前核对")
    print("=" * 64)

    print("\n[1] 必交文档（CHALLENGE.md §必须提交的文件）")
    for f in REQUIRED_DOCS:
        p = ROOT / f
        if not p.exists():
            check(f, False, "文件不存在")
        elif p.stat().st_size == 0:
            check(f, False, "文件为空")
        else:
            check(f"{f}（{p.stat().st_size:,} 字节）", True)

    print("\n[2] 可运行技能包")
    skill = ROOT / "卢怡然_C4C_homework-solver.skill"
    if not skill.exists():
        check("卢怡然_C4C_homework-solver.skill", False, "不存在")
    else:
        man_p = ROOT / "evidence" / "skill_manifest.json"
        if not man_p.exists():
            check("evidence/skill_manifest.json", False, "不存在")
        else:
            man = json.loads(man_p.read_text(encoding="utf-8"))
            same = sha256(skill) == man["skill_sha256"]
            check(f".skill 与 manifest 记录的 sha256 一致（{skill.stat().st_size:,} 字节）",
                  same, "" if same else f"实际 {sha256(skill)[:16]}… vs 记录 "
                                        f"{man['skill_sha256'][:16]}…")

        # 包内的 .skill 必须含关键文件，不含 __pycache__
        import zipfile
        with zipfile.ZipFile(skill) as z:
            names = z.namelist()
            bad_cache = [n for n in names if "__pycache__" in n]
            check("包内无 __pycache__", not bad_cache, f"{len(bad_cache)} 个")
            for need in ("homework-solver/SKILL.md",
                         "homework-solver/scripts/pipeline.py",
                         "homework-solver/scripts/llm_client.py",
                         "homework-solver/scripts/solvers_linalg.py",
                         "homework-solver/domain_skills/linear_algebra.yaml"):
                check(f"包内含 {need.split('/')[-1]}", need in names)

    print("\n[3] 证据留档")
    for f in ("evidence/selftest_run.txt",
              "evidence/run/3_solutions.json",
              "evidence/run/run_report.json",
              "evidence/run/homework.pdf",
              "evidence/skill_manifest.json"):
        p = ROOT / f
        check(f, p.exists() and p.stat().st_size > 0)

    print("\n[4] 一致性")
    ok = True
    a = ROOT / "卢怡然_C4C_output.pdf"
    b = ROOT / "evidence" / "run" / "homework.pdf"
    if a.exists() and b.exists():
        ok = check("output.pdf 与 evidence/run/homework.pdf 字节一致",
                   sha256(a) == sha256(b))
    rep_p = ROOT / "evidence" / "run" / "run_report.json"
    if rep_p.exists():
        rep = json.loads(rep_p.read_text(encoding="utf-8"))
        st = rep.get("stage5") or {}
        n_ok = sum(1 for c in st.get("checks", []) if c.get("ok"))
        ok &= check(f"run_report 的 Stage5 验证 {n_ok}/{len(st.get('checks', []))} 项通过",
                    bool(st.get("ok")))
    sel = (ROOT / "evidence" / "selftest_run.txt")
    if sel.exists():
        txt = sel.read_text(encoding="utf-8")
        import re
        m = re.search(r"结果: (\d+)/(\d+) 项通过", txt)
        if m:
            ok &= check(f"自检输出为 {m.group(1)}/{m.group(2)}", m.group(1) == m.group(2))
        else:
            check("自检输出含结论行", False)

    print("\n[5] 基线黄金")
    gd = ROOT / "homework-solver" / "tests" / "golden"
    mp = gd / "MANIFEST.json"
    if mp.exists():
        man = json.loads(mp.read_text(encoding="utf-8"))
        for name, meta in man["records"].items():
            p = gd / name
            if not p.exists():
                check(f"golden/{name}", False, "缺失")
                continue
            digest = hashlib.sha256(json.dumps(
                json.loads(p.read_text(encoding="utf-8")),
                ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
            check(f"golden/{name} 未被污染", digest == meta["sha256"])
    else:
        check("golden/MANIFEST.json", False, "不存在（跑 tests/record_golden.py）")

    print("\n[6] 诚实性：不许存在会误导的残留")
    # 空的 llm_calls.jsonl 会让人以为"调用过但没记录"；
    # 缺文件时必须有说明文件。
    note = ROOT / "evidence" / "run" / "关于_llm_calls.jsonl的说明.md"
    llm = ROOT / "evidence" / "run" / "llm_calls.jsonl"
    if not llm.exists():
        check("无 LLM 调用留档时已附说明文件", note.exists(),
              "" if note.exists() else "缺 关于_llm_calls.jsonl的说明.md")
    else:
        lines = [l for l in llm.read_text(encoding="utf-8").splitlines() if l.strip()]
        check(f"llm_calls.jsonl 含 {len(lines)} 条真实调用", len(lines) > 0)

    n = len(RESULTS)
    passed = sum(1 for r in RESULTS if r[0])
    print("\n" + "=" * 64)
    print(f"结果: {passed}/{n} 项通过")
    for okk, name, detail in RESULTS:
        if not okk:
            print(f"  未通过: {name} — {detail}")
    print("=" * 64)
    sys.exit(0 if passed == n else 1)


if __name__ == "__main__":
    main()
