# run_bench.py
import argparse
import csv
import re
import statistics as stats
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

DEFAULT_SIZES = [20, 25, 50, 80, 100]

TIME_PATTERNS = [
    re.compile(r"(time|elapsed|took|runtime)\s*[:=]?\s*([0-9]*\.?[0-9]+)\s*(ms|s|sec|secs|seconds)?", re.I),
    re.compile(r"\b([0-9]*\.?[0-9]+)\s*(ms|s|sec|secs|seconds)\b", re.I),
]

def parse_time_from_output(text: str):
    candidates = []
    for pat in TIME_PATTERNS:
        for m in pat.finditer(text):
            if len(m.groups()) == 3:
                val = m.group(2)
                unit = m.group(3) or "s"
            else:
                val = m.group(1)
                unit = m.group(2) or "s"

            try:
                x = float(val)
            except:
                continue

            unit = unit.lower()
            if unit.startswith("ms"):
                x /= 1000.0
            if x > 0:
                candidates.append(x)
    return min(candidates) if candidates else None

def run_script_with_inputfile(python_exe: str, script_path: Path, input_file: Path, timeout: int):
    input_text = input_file.read_text(encoding="utf-8", errors="ignore")
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            [python_exe, str(script_path)],
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        wall = time.perf_counter() - t0
        out = p.stdout or ""
        err = p.stderr or ""
        parsed = parse_time_from_output(out + "\n" + err)
        runtime = parsed if parsed is not None else wall
        return {
            "returncode": p.returncode,
            "stdout": out,
            "stderr": err,
            "wall_seconds": wall,
            "parsed_seconds": parsed,
            "runtime_seconds": runtime,
        }
    except subprocess.TimeoutExpired as e:
        wall = time.perf_counter() - t0
        return {
            "returncode": 124,
            "stdout": e.stdout or "",
            "stderr": (e.stderr or "") + "\n[TIMEOUT]",
            "wall_seconds": wall,
            "parsed_seconds": None,
            "runtime_seconds": wall,
        }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=str, default=".", help="Root folder containing scripts and testcase folder")
    ap.add_argument("--tests", type=str, default="testcases", help="Folder containing data_size_*.txt files")
    ap.add_argument("--repeats", type=int, default=5, help="Runs per testcase per script")
    ap.add_argument("--timeout", type=int, default=600, help="Timeout seconds per run")
    ap.add_argument("--python", type=str, default=sys.executable, help="Python executable")
    ap.add_argument("--sizes", type=str, default=",".join(map(str, DEFAULT_SIZES)),
                    help="Comma-separated sizes: 9,10,11,...")
    ap.add_argument("--out", type=str, default="", help="Output text file (single). Default auto name.")
    ap.add_argument("--write-csv", action="store_true", help="Also write results_summary.csv next to output file.")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    tests_dir = (root / args.tests).resolve()

    scripts = [root / "local_greedy.py", root / "multi_greedy.py"]
    for s in scripts:
        if not s.exists():
            print(f"[ERROR] Missing script: {s}")
            sys.exit(1)

    if not tests_dir.exists():
        print(f"[ERROR] Missing tests folder: {tests_dir}")
        sys.exit(1)

    sizes = [int(x.strip()) for x in args.sizes.split(",") if x.strip()]
    testcase_files = [tests_dir / f"data_size_{n}.txt" for n in sizes]
    missing = [f for f in testcase_files if not f.exists()]
    if missing:
        print("[ERROR] Missing testcase files:")
        for m in missing:
            print(" -", m)
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = Path(args.out).resolve() if args.out else (root / f"all_outputs_{ts}.txt")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    with out_file.open("w", encoding="utf-8", errors="ignore") as fout:
        fout.write(f"BENCH OUTPUTS\n")
        fout.write(f"generated_at: {datetime.now().isoformat()}\n")
        fout.write(f"root: {root}\n")
        fout.write(f"tests_dir: {tests_dir}\n")
        fout.write(f"repeats: {args.repeats}\n")
        fout.write(f"timeout_s: {args.timeout}\n")
        fout.write(f"python: {args.python}\n")
        fout.write("=" * 80 + "\n\n")

        for tc in testcase_files:
            for script in scripts:
                for rep in range(1, args.repeats + 1):
                    header = f"[TESTCASE={tc.name}] [SCRIPT={script.name}] [REP={rep}]"
                    print("[RUN]", header)

                    res = run_script_with_inputfile(args.python, script, tc, args.timeout)

                    rows.append({
                        "testcase": tc.name,
                        "script": script.name,
                        "rep": rep,
                        "returncode": res["returncode"],
                        "runtime_seconds": res["runtime_seconds"],
                        "wall_seconds": res["wall_seconds"],
                        "parsed_seconds": "" if res["parsed_seconds"] is None else res["parsed_seconds"],
                    })

                    fout.write("=" * 80 + "\n")
                    fout.write(header + "\n")
                    fout.write(f"returncode: {res['returncode']}\n")
                    fout.write(f"runtime_seconds: {res['runtime_seconds']:.6f}\n")
                    fout.write(f"wall_seconds: {res['wall_seconds']:.6f}\n")
                    fout.write(f"parsed_seconds: {res['parsed_seconds']}\n")
                    fout.write("-" * 80 + "\n")
                    fout.write("[STDOUT]\n")
                    fout.write(res["stdout"] + ("\n" if not res["stdout"].endswith("\n") else ""))
                    fout.write("[STDERR]\n")
                    fout.write(res["stderr"] + ("\n" if not res["stderr"].endswith("\n") else ""))
                    fout.write("\n")

        # Summary in the SAME file
        fout.write("\n" + "#" * 80 + "\n")
        fout.write("SUMMARY (only returncode==0)\n")
        fout.write("#" * 80 + "\n")

        def key_sort(x):
            # sort by numeric size if possible
            m = re.search(r"data_size_(\d+)", x)
            return int(m.group(1)) if m else x

        testcases_sorted = sorted(set(r["testcase"] for r in rows), key=key_sort)
        scripts_sorted = sorted(set(r["script"] for r in rows))

        for tc_name in testcases_sorted:
            fout.write(f"\n== {tc_name} ==\n")
            for sc in scripts_sorted:
                ok = [r for r in rows if r["testcase"] == tc_name and r["script"] == sc and r["returncode"] == 0]
                runtimes = [r["runtime_seconds"] for r in ok]
                if not runtimes:
                    fout.write(f"- {sc}: ok_runs=0\n")
                    continue
                fout.write(
                    f"- {sc}: ok_runs={len(runtimes)}, "
                    f"mean={stats.mean(runtimes):.6f}s, "
                    f"median={stats.median(runtimes):.6f}s, "
                    f"min={min(runtimes):.6f}s, "
                    f"max={max(runtimes):.6f}s\n"
                )

    # optional CSV summary
    if args.write_csv:
        summary_csv = out_file.with_name(out_file.stem + "_summary.csv")
        summary_rows = []
        for tc in sorted(set(r["testcase"] for r in rows), key=key_sort):
            for sc in sorted(set(r["script"] for r in rows)):
                ok = [r for r in rows if r["testcase"] == tc and r["script"] == sc and r["returncode"] == 0]
                runtimes = [r["runtime_seconds"] for r in ok]
                if runtimes:
                    summary_rows.append({
                        "testcase": tc,
                        "script": sc,
                        "ok_runs": len(runtimes),
                        "mean_s": stats.mean(runtimes),
                        "median_s": stats.median(runtimes),
                        "min_s": min(runtimes),
                        "max_s": max(runtimes),
                        "stdev_s": (stats.pstdev(runtimes) if len(runtimes) > 1 else 0.0),
                    })
                else:
                    summary_rows.append({
                        "testcase": tc,
                        "script": sc,
                        "ok_runs": 0,
                        "mean_s": "",
                        "median_s": "",
                        "min_s": "",
                        "max_s": "",
                        "stdev_s": "",
                    })

        with summary_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)

        print("[CSV] wrote:", summary_csv)

    print("\n[DONE] wrote single output file:", out_file)

if __name__ == "__main__":
    main()
