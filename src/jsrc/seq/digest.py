import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO
from Bio.Restriction import AllEnzymes, RestrictionBatch

logger = logging.getLogger(__name__)


def _calc_fragments(
    cut_positions: list[int], seq_length: int, circular: bool
) -> list[int]:
    positions = sorted(set(cut_positions))
    if not positions:
        return [seq_length]

    if circular:
        fragments = []
        for i in range(len(positions)):
            start = positions[i]
            end = positions[(i + 1) % len(positions)]
            if i == len(positions) - 1:
                end += seq_length
            fragments.append(end - start)
    else:
        boundaries = [0] + positions + [seq_length]
        fragments = [
            boundaries[i + 1] - boundaries[i] for i in range(len(boundaries) - 1)
        ]

    return sorted(fragments, reverse=True)


def cmd(args: Namespace) -> None:
    records = list(SeqIO.parse(args.fa, "fasta"))
    if not records:
        raise SystemExit("No sequences found in input")

    enzyme_names = [e.strip() for e in args.enzymes.split(",") if e.strip()]
    if not enzyme_names:
        raise SystemExit("No enzymes specified")

    target = records[0]
    seq = target.seq

    known = {str(e) for e in AllEnzymes}
    valid: list[str] = []
    unrecognized: list[str] = []
    for name in enzyme_names:
        (valid if name in known else unrecognized).append(name)

    if valid:
        rb = RestrictionBatch(valid)
        results = rb.search(seq)
    else:
        results = {}

    if unrecognized:
        logger.warning("Unrecognized enzymes (skipped): %s", ", ".join(unrecognized))

    all_cuts: set[int] = set()
    for positions in results.values():
        all_cuts.update(positions)

    fragments = _calc_fragments(sorted(all_cuts), len(seq), args.circular)

    mode = "circular" if args.circular else "linear"
    info = (
        f"Digesting {target.id} ({len(seq)} bp, {mode}) "
        f"with {', '.join(valid or enzyme_names)}"
    )
    logger.info(info)

    if args.min_size:
        filtered = [f for f in fragments if f >= args.min_size]
        logger.info(
            "%s digestion: %d fragment(s) (%d >= %d bp)",
            mode,
            len(filtered),
            len(fragments),
            args.min_size,
        )
    else:
        filtered = fragments
        logger.info("%s digestion: %d fragment(s)", mode, len(filtered))

    if args.json:
        payload = {
            "sequence_id": target.id,
            "sequence_length": len(seq),
            "mode": mode,
            "enzymes": enzyme_names,
            "cut_positions": sorted(all_cuts),
            "total_fragments": len(fragments),
            "fragment_sizes": fragments,
        }
        if args.min_size:
            payload["min_size_filter"] = args.min_size
            payload["filtered_fragment_sizes"] = filtered
        print(json.dumps(payload, indent=2))
    else:
        header = (
            f"Digest of {target.id} " f"({mode}, {', '.join(valid or enzyme_names)})"
        )
        print(header)
        print("-" * len(header))
        for i, size in enumerate(filtered, 1):
            print(f"{i}.\t{size} bp")
        if args.min_size and len(filtered) < len(fragments):
            omitted = len(fragments) - len(filtered)
            print(f"\n({omitted} fragment(s) < {args.min_size} bp omitted)")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("digest", help="Simulate restriction enzyme digestion")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument(
        "-e", "--enzymes", required=True, help="Comma-separated enzyme names"
    )
    p.add_argument(
        "--circular",
        action="store_true",
        help="Treat sequence as circular",
    )
    p.add_argument(
        "--min-size",
        type=int,
        default=0,
        help="Minimum fragment size to report",
    )
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
