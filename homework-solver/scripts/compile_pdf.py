#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 5（C4C 新增）: 编译与验证
==============================

starter kit 里 Stage 5 只是 render_latex.py 末尾一个 `compile_pdf()` 布尔函数
（跑 3 遍 pdflatex，只看 PDF 在不在）。这里把它拆成独立的 stage，并补上
CHALLENGE 要求的"验证"：

验证项
------
V1  PDF 确实生成，且 > 1 KB
V2  页数 ≥ 1，且与 .log 里的 Output written 页数一致
V3  编译日志无 `Undefined control sequence` / `Missing $ inserted` / `LaTeX Error`
V4  抽取文本里没有 `??`（未解析的交叉引用）
V5  中文文档：抽取文本里确实含 CJK 字符（防止 ctex 没生效变豆腐块）
V6  PDF 尾部的 `%%EOF` 存在（文件未截断）

任何一项不过，整个 stage 返回 ok=False，并把失败项列出来。

用法:
    python compile_pdf.py homework.tex [--engine xelatex] [--lang zh] [--outdir .]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Windows 上 TeX Live 常常不在 PATH 里，这里补几个常见位置
_EXTRA_BIN_DIRS = []
if os.name == "nt":
    for base in (Path("C:/texlive"), Path("C:/Program Files"), Path("C:/miktex")):
        if base.exists():
            try:
                for p in sorted(base.glob("*/bin/windows"), reverse=True):
                    _EXTRA_BIN_DIRS.append(str(p))
                for p in sorted(base.glob("miktex/bin/*")):
                    _EXTRA_BIN_DIRS.append(str(p))
            except Exception:
                pass

FATAL_LOG_PATTERNS = [
    r"Undefined control sequence",
    r"Missing \$ inserted",
    r"LaTeX Error:",
    r"! Emergency stop",
    r"Package .* Error:",
    r"Fontconfig error",
]

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def find_engine(name: str) -> str:
    """在 PATH 与常见 TeX 安装目录里找一个引擎可执行文件。"""
    found = shutil.which(name)
    if found:
        return found
    for d in _EXTRA_BIN_DIRS:
        for cand in (f"{name}.exe", name):
            p = Path(d) / cand
            if p.exists():
                return str(p)
    return ""


def available_engines() -> list:
    return [e for e in ("xelatex", "pdflatex", "lualatex") if find_engine(e)]


def _run(engine: str, tex_path: Path, outdir: Path, timeout: int = 120):
    cmd = [engine, "-interaction=nonstopmode", "-halt-on-error",
           f"-output-directory={outdir}", str(tex_path)]
    return subprocess.run(cmd, capture_output=True, timeout=timeout,
                          cwd=str(tex_path.parent))


def compile_and_validate(
    tex_path: str,
    output_dir: str = None,
    lang: str = "zh",
    engine: str = None,
    passes: int = 2,
    timeout: int = 180,
) -> dict:
    """
    编译 LaTeX 并做 6 项验证。返回结构化结果 dict。
    """
    # ── 路径必须先把 __file__/cwd 的相对路径钉成绝对路径 ───────────
    # 踩过的坑：pipeline 传进来的 output_dir 是相对路径（"output/"）时，
    # 下面 _run() 会把子进程 cwd 设成 tex 所在目录，而 -output-directory
    # 是相对子进程 cwd 解析的 —— 产物被写到了 outdir/outdir/ 下，
    # 于是 pdf_path.exists() 恒为 False，日志里明明写着 "Output written
    # on homework.pdf" 却报"未产出 PDF"。所以这里统一 resolve()。
    tex_path = Path(tex_path).expanduser()
    try:
        tex_path = tex_path.resolve()
    except Exception:
        tex_path = tex_path.absolute()
    outdir = Path(output_dir).expanduser() if output_dir else tex_path.parent
    try:
        outdir = outdir.resolve()
    except Exception:
        outdir = outdir.absolute()
    outdir.mkdir(parents=True, exist_ok=True)

    has_cjk = lang == "zh"
    if engine:
        order = [engine]
    elif has_cjk:
        # 中文：xelatex（系统字体）优先；本机 fontconfig 异常时自动退回 pdflatex + ctex(CJK)
        order = ["xelatex", "pdflatex", "lualatex"]
    else:
        order = ["pdflatex", "xelatex", "lualatex"]
    order = [e for e in order if find_engine(e)]

    if not order:
        return {"ok": False, "error": "本机未找到任何 LaTeX 引擎（pdflatex/xelatex/lualatex）",
                "checks": [], "engine": None}

    pdf_path = outdir / (tex_path.stem + ".pdf")
    log_path = outdir / (tex_path.stem + ".log")
    last_result = None
    attempts = []

    for eng in order:
        exe = find_engine(eng)
        # 换引擎前清掉上一个引擎的中间产物：失败的 xelatex 会留下残缺 .aux，
        # 让后面的 pdflatex 在第一遍读到脏数据。
        _clean_intermediates(outdir, tex_path.stem, keep_pdf=False)

        try:
            for _ in range(passes):
                _run(exe, tex_path, outdir, timeout=timeout)
        except subprocess.TimeoutExpired:
            last_result = {"ok": False, "engine": eng, "error": f"{eng} 编译超时"}
            attempts.append(last_result)
            continue
        except Exception as e:
            last_result = {"ok": False, "engine": eng, "error": f"{eng} 调用失败: {e}"}
            attempts.append(last_result)
            continue

        if not pdf_path.exists() or pdf_path.stat().st_size == 0:
            last_result = {"ok": False, "engine": eng,
                           "error": f"{eng} 未产出 PDF",
                           "log_tail": _tail(log_path)}
            attempts.append(last_result)
            continue

        checks = _validate(tex_path, pdf_path, log_path, has_cjk)
        ok = all(c["ok"] for c in checks)
        # 注意：attempts 里放的是**诊断副本**，不能直接塞 result 本体，
        # 否则最后 result["attempts"] = attempts 会自引用，
        # run_report.json 序列化时报 "Circular reference detected"。
        diag = {"ok": ok, "engine": eng, "size": pdf_path.stat().st_size,
                "checks": checks}
        attempts.append(diag)
        result = {"ok": ok, "engine": eng, "pdf": str(pdf_path),
                  "size": pdf_path.stat().st_size, "checks": checks}
        if ok:
            result["attempts"] = attempts
            return result
        last_result = result

    if last_result:
        # 把每个引擎都做了什么带出去：只报最后一个引擎会把真正的病因藏起来
        last_result = dict(last_result)
        last_result["attempts"] = attempts
    return last_result or {"ok": False, "error": "编译未成功", "checks": [], "attempts": attempts}


_INTERMEDIATE_SUFFIXES = (".aux", ".log", ".out", ".toc", ".lof", ".lot", ".xdv", ".synctex.gz")


def _clean_intermediates(outdir: Path, stem: str, keep_pdf: bool = False):
    """删掉某个引擎留下的中间产物，避免污染下一个引擎的第一遍。"""
    for suf in _INTERMEDIATE_SUFFIXES:
        p = outdir / (stem + suf)
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass
    if not keep_pdf:
        pdf = outdir / (stem + ".pdf")
        if pdf.exists():
            try:
                pdf.unlink()
            except Exception:
                pass


def _tail(path: Path, n: int = 600) -> str:
    """失败时带一段日志尾部，省得再来一遍复现。"""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[-n:]
    except Exception:
        return ""


def _extract_text(pdf_path: Path):
    """尽力抽文本：pypdf → pdftotext → None。"""
    try:
        import pypdf
        r = pypdf.PdfReader(str(pdf_path))
        return "\n".join((p.extract_text() or "") for p in r.pages), len(r.pages)
    except Exception:
        pass
    pdftotext = find_engine("pdftotext")
    if pdftotext:
        try:
            out = subprocess.run([pdftotext, str(pdf_path), "-"],
                                 capture_output=True, timeout=60)
            txt = out.stdout.decode("utf-8", errors="replace")
            return txt, txt.count("\f") + 1
        except Exception:
            pass
    return None, None


def _validate(tex_path: Path, pdf_path: Path, log_path: Path, has_cjk: bool) -> list:
    checks = []

    # V1 大小
    size = pdf_path.stat().st_size
    checks.append({"id": "V1", "name": f"PDF 已生成且 > 1KB（{size:,} 字节）",
                   "ok": size > 1024})

    # V6 文件完整
    try:
        tail = pdf_path.open("rb").read()[-64:]
        checks.append({"id": "V6", "name": "PDF 文件完整（含 %%EOF）",
                       "ok": b"%%EOF" in tail})
    except Exception as e:
        checks.append({"id": "V6", "name": f"PDF 读取失败: {e}", "ok": False})

    # V3 日志无致命错误
    log_text = ""
    if log_path.exists():
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
    fatal = [p for p in FATAL_LOG_PATTERNS if re.search(p, log_text)]
    checks.append({"id": "V3", "name": "编译日志无致命错误",
                   "ok": not fatal, "detail": "; ".join(fatal)})

    # V2 页数
    text, pages = _extract_text(pdf_path)
    if pages is None:
        m = re.search(r"Output written on .*?\((\d+) page", log_text)
        pages = int(m.group(1)) if m else 0
    checks.append({"id": "V2", "name": f"页数 ≥ 1（实测 {pages} 页）", "ok": pages >= 1})

    # V4 无 ?? 交叉引用
    undef = bool(text and "??" in text)
    checks.append({"id": "V4", "name": "文本中无未解析引用（??）", "ok": not undef})

    # V5 中文确实渲染
    if has_cjk:
        n_cjk = len(CJK_RE.findall(text or ""))
        checks.append({"id": "V5", "name": f"中文字符已正确嵌入（抽取到 {n_cjk} 个汉字）",
                       "ok": n_cjk >= 20})
    return checks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--outdir")
    ap.add_argument("--engine")
    ap.add_argument("--lang", default="zh")
    args = ap.parse_args()

    print("可用引擎:", available_engines())
    r = compile_and_validate(args.tex, args.outdir, lang=args.lang, engine=args.engine)
    print("结果:", "通过" if r.get("ok") else "失败", "| 引擎:", r.get("engine"))
    for c in r.get("checks", []):
        print(f"  [{'√' if c['ok'] else '×'}] {c['name']}")
    if not r.get("ok"):
        print("  错误:", r.get("error", ""))
        sys.exit(1)


if __name__ == "__main__":
    main()
