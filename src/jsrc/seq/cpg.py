import json
from argparse import Namespace
from typing import Any

from Bio import SeqIO


def _cpg_islands(
    seq: str, window: int, step: int, min_len: int, min_gc: float, min_oe: float
) -> list[dict[str, Any]]:
    seq = seq.upper().replace("U", "T")
    n = len(seq)
    islands: list[tuple[int, int]] = []
    in_island = False
    island_start = 0

    for i in range(0, max(1, n - window + 1), step):
        sub = seq[i:i + window]
        if len(sub) < window:
            break
        c_count = sub.count("C")
        g_count = sub.count("G")
        gc = c_count + g_count
        gc_pct = gc / window
        cg_obs = sub.count("CG")
        cg_exp = (c_count * g_count) / window if window > 0 else 0
        oe = cg_obs / cg_exp if cg_exp > 0 else 0.0

        qualifies = gc_pct >= min_gc and oe >= min_oe
        if qualifies and not in_island:
            in_island = True
            island_start = i
        elif not qualifies and in_island:
            in_island = False
            islands.append((island_start, i + window - step))
    if in_island:
        islands.append((island_start, n))

    results = []
    for start, end in islands:
        if end - start < min_len:
            continue
        sub = seq[start:end]
        length = end - start
        c_count = sub.count("C")
        g_count = sub.count("G")
        gc_pct = (c_count + g_count) / length
        cg_obs = sub.count("CG")
        cg_exp = (c_count * g_count) / length if length > 0 else 0
        oe = cg_obs / cg_exp if cg_exp > 0 else 0.0
        results.append({
            "start": start + 1,
            "end": end,
            "length": length,
            "gc_percent": round(gc_pct * 100, 4),
            "obs_exp_cpg": round(oe, 4),
            "cpg_count": cg_obs,
        })
    return results


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise SystemExit("No sequences found in FASTA")
    all_results = []
    for rec in records:
        islands = _cpg_islands(
            str(rec.seq), args.window, args.step,
            args.min_len, args.min_gc / 100.0, args.min_oe,
        )
        for isl in islands:
            isl["seq_id"] = rec.id
        all_results.extend(islands)

    if args.json:
        print(json.dumps(all_results, ensure_ascii=False, indent=2))
        return
    print("seq_id\tstart\tend\tlength\tgc_percent\tobs_exp_cpg\tcpg_count")
    for r in all_results:
        print(f"{r['seq_id']}\t{r['start']}\t{r['end']}\t{r['length']}\t"
              f"{r['gc_percent']}\t{r['obs_exp_cpg']}\t{r['cpg_count']}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("cpg", help="Predict CpG islands")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("--window", type=int, default=200, help="Window size (default: 200)")
    p.add_argument("--step", type=int, default=1, help="Step size (default: 1)")
    p.add_argument("--min-len", type=int, default=500,
                   help="Minimum island length bp (default: 500)")
    p.add_argument("--min-gc", type=float, default=50.0,
                   help="Minimum GC percent (default: 50.0)")
    p.add_argument("--min-oe", type=float, default=0.6,
                   help="Minimum observed/expected CpG ratio (default: 0.6)")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
