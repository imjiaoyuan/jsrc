from __future__ import annotations

import json
from argparse import Namespace
from collections.abc import Iterator
from typing import Any

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

from jsrc.core import DataFormatError, ValidationError
from jsrc.genome.core import normalize_sequence


def _pick_record(path: str, seq_id: str | None) -> SeqRecord:
    if seq_id:
        for rec in SeqIO.parse(path, "fasta"):
            if rec.id == seq_id or rec.id.split()[0] == seq_id:
                return rec
        raise DataFormatError(f"Sequence ID not found: {seq_id}")
    longest: SeqRecord | None = None
    for rec in SeqIO.parse(path, "fasta"):
        rec_seq = rec.seq
        longest_seq = longest.seq if longest else None
        if longest is None or (
            rec_seq is not None
            and longest_seq is not None
            and len(rec_seq) > len(longest_seq)
        ):
            longest = rec
    if longest is None:
        raise DataFormatError("No sequences found in FASTA")
    return longest


def _iter_windows(seq: str, w: int, s: int) -> Iterator[dict[str, float | int]]:
    seq = normalize_sequence(seq)
    for start in range(0, max(1, len(seq) - w + 1), s):
        end = min(start + w, len(seq))
        sub = seq[start:end]
        a = sub.count("A")
        t = sub.count("T")
        g = sub.count("G")
        c = sub.count("C")
        gc = g + c
        at = a + t
        gc_pct = gc / len(sub) * 100.0 if sub else 0.0
        at_skew = (a - t) / at if at else 0.0
        gc_skew = (g - c) / gc if gc else 0.0
        yield {
            "start": start + 1,
            "end": end,
            "len": len(sub),
            "gc_percent": gc_pct,
            "at_skew": at_skew,
            "gc_skew": gc_skew,
        }
        if end >= len(seq):
            break


def _calculate_cumulative_gc_skew(
    seq: str, window: int, step: int
) -> list[dict[str, Any]]:
    """Per-window GC skew plus a running cumulative skew (for origin prediction)."""
    seq = normalize_sequence(seq)
    n = len(seq)
    results: list[dict[str, Any]] = []
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


def _cmd_cumulative(args: Namespace, rec: SeqRecord, rec_seq: str) -> None:
    skew_data = _calculate_cumulative_gc_skew(rec_seq, args.w, args.s)
    min_point, max_point = _find_skew_extrema(skew_data)
    output_data = skew_data[: args.head] if args.head > 0 else skew_data

    result = {
        "sequence_id": rec.id,
        "sequence_length": len(rec_seq),
        "window_size": args.w,
        "step_size": args.s,
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


def cmd(args: Namespace) -> None:
    if args.w < 1 or args.s < 1:
        raise ValidationError("-w and -s must be >= 1")
    rec = _pick_record(args.fa, args.id)
    rec_seq = str(rec.seq if rec.seq is not None else "")

    if args.cumulative:
        _cmd_cumulative(args, rec, rec_seq)
        return

    window_count = 0
    windows_head: list[dict[str, float | int]] = []
    head_limit = max(0, args.head)
    for row in _iter_windows(rec_seq, args.w, args.s):
        window_count += 1
        if len(windows_head) < head_limit:
            windows_head.append(row)
    payload = {
        "sequence_id": rec.id,
        "sequence_length": len(rec_seq),
        "window_size": args.w,
        "step_size": args.s,
        "window_count": window_count,
        "windows_head": windows_head,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"sequence_id\t{payload['sequence_id']}")
    print(f"sequence_length\t{payload['sequence_length']:,}")
    print(f"window_size\t{payload['window_size']}")
    print(f"step_size\t{payload['step_size']}")
    print(f"window_count\t{payload['window_count']:,}")
    print("start\tend\tlen\tgc_percent\tat_skew\tgc_skew")
    for row in payload["windows_head"]:
        print(
            f"{row['start']}\t{row['end']}\t{row['len']}\t"
            f"{row['gc_percent']:.4f}\t{row['at_skew']:.6f}\t{row['gc_skew']:.6f}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("window", help="Sliding-window GC and AT skew")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument("-id", help="Target sequence ID (default: longest sequence)")
    p.add_argument("-w", type=int, default=1000, help="Window size")
    p.add_argument("-s", type=int, default=200, help="Step size")
    p.add_argument("--head", type=int, default=10, help="Print first N windows")
    p.add_argument(
        "--cumulative",
        action="store_true",
        help="Cumulative GC skew + replication origin/terminus prediction",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
