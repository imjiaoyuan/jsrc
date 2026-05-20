import json
from argparse import Namespace
from typing import Any

from Bio import SeqIO

from jsrc.genome.core import normalize_sequence


def _calculate_cumulative_gc_skew(
    seq: str, window: int, step: int
) -> list[dict[str, Any]]:
    seq = normalize_sequence(seq)
    n = len(seq)
    results = []
    cumulative_skew = 0.0

    for i in range(0, max(1, n - window + 1), step):
        sub = seq[i : i + window]
        if len(sub) < window:
            break
        g = sub.count("G")
        c = sub.count("C")
        gc = g + c
        skew = (g - c) / gc if gc > 0 else 0.0
        cumulative_skew += skew

        results.append(
            {
                "position": i + 1,
                "window_start": i + 1,
                "window_end": min(i + window, n),
                "gc_skew": round(skew, 6),
                "cumulative_gc_skew": round(cumulative_skew, 6),
                "g_count": g,
                "c_count": c,
            }
        )

    return results


def _find_skew_extrema(
    data: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not data:
        return None, None

    min_point = min(data, key=lambda x: x["cumulative_gc_skew"])
    max_point = max(data, key=lambda x: x["cumulative_gc_skew"])

    return min_point, max_point


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise SystemExit("No sequences found in FASTA")

    if args.id:
        rec = next((r for r in records if r.id == args.id), None)
        if rec is None:
            raise SystemExit(f"Sequence ID not found: {args.id}")
    else:
        rec = max(records, key=lambda r: len(r.seq))

    skew_data = _calculate_cumulative_gc_skew(str(rec.seq), args.window, args.step)
    min_point, max_point = _find_skew_extrema(skew_data)

    output_data = skew_data[: args.head] if args.head > 0 else skew_data

    result = {
        "sequence_id": rec.id,
        "sequence_length": len(rec.seq),
        "window_size": args.window,
        "step_size": args.step,
        "data_points": len(skew_data),
        "min_skew_position": min_point["position"] if min_point else None,
        "min_skew_value": min_point["cumulative_gc_skew"] if min_point else None,
        "max_skew_position": max_point["position"] if max_point else None,
        "max_skew_value": max_point["cumulative_gc_skew"] if max_point else None,
        "skew_data": output_data,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"sequence_id\t{result['sequence_id']}")
    print(f"sequence_length\t{result['sequence_length']:,}")
    print(f"window_size\t{result['window_size']}")
    print(f"step_size\t{result['step_size']}")
    print(f"data_points\t{result['data_points']:,}")
    print()
    print("Predicted replication origin (minimum cumulative GC skew):")
    if min_point:
        print(f"  Position: {min_point['position']:,} bp")
        print(f"  Cumulative GC skew: {min_point['cumulative_gc_skew']:.6f}")
    print()
    print("Predicted replication terminus (maximum cumulative GC skew):")
    if max_point:
        print(f"  Position: {max_point['position']:,} bp")
        print(f"  Cumulative GC skew: {max_point['cumulative_gc_skew']:.6f}")
    print()
    print(
        "position\twindow_start\twindow_end\tgc_skew\tcumulative_gc_skew\tg_count\tc_count"
    )
    for row in output_data:
        print(
            f"{row['position']}\t{row['window_start']}\t{row['window_end']}\t"
            f"{row['gc_skew']}\t{row['cumulative_gc_skew']}\t{row['g_count']}\t{row['c_count']}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "gc-skew",
        help="Cumulative GC skew analysis for replication origin prediction",
    )
    p.add_argument("-fa", required=True, help="Input genome FASTA file")
    p.add_argument("-id", help="Sequence ID (default: longest sequence)")
    p.add_argument(
        "-w", "--window", type=int, default=10000, help="Window size (default: 10000)"
    )
    p.add_argument(
        "-s", "--step", type=int, default=1000, help="Step size (default: 1000)"
    )
    p.add_argument(
        "--head", type=int, default=20, help="Show first N data points (0 = all)"
    )
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
