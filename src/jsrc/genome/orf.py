from __future__ import annotations

import json
import logging
from argparse import Namespace
from typing import Any

from jsrc.core import load_fasta
from jsrc.genome.core import AA_TABLE as _CODON_TABLE

logger = logging.getLogger(__name__)


def _find_orfs(seq: str, min_len: int, all_frames: bool) -> list[dict[str, Any]]:
    seq = seq.upper().replace("U", "T")
    n = len(seq)
    results = []
    frames = [0, 1, 2] if all_frames else [0]
    for frame in frames:
        i = frame
        while i <= n - 3:
            codon = seq[i : i + 3]
            if codon == "ATG":
                found_stop = False
                for j in range(i, n - 2, 3):
                    c = seq[j : j + 3]
                    if len(c) < 3:
                        break
                    aa = _CODON_TABLE.get(c, "X")
                    if aa == "*":
                        orf_nt = seq[i : j + 3]
                        length = len(orf_nt)
                        if length >= min_len:
                            protein = "".join(
                                _CODON_TABLE.get(orf_nt[k : k + 3], "X")
                                for k in range(0, length - 3, 3)
                            )
                            results.append(
                                {
                                    "start": i + 1,
                                    "end": j + 3,
                                    "length": length,
                                    "frame": frame + 1,
                                    "strand": "+",
                                    "protein": protein,
                                }
                            )
                        i = j + 3
                        found_stop = True
                        break
                if not found_stop:
                    i += 3
            else:
                i += 3
    return sorted(results, key=lambda x: x["length"], reverse=True)


def cmd(args: Namespace) -> None:
    records = load_fasta(args.fa)
    all_orfs = []
    for rec in records:
        seq = str(rec.seq).upper().replace("U", "T")
        orfs = _find_orfs(seq, args.min_len, args.all_frames)
        for orf in orfs:
            orf["seq_id"] = rec.id
        if args.top:
            orfs = orfs[: args.top]
        all_orfs.extend(orfs)

    if args.json:
        print(json.dumps(all_orfs, ensure_ascii=False, indent=2))
        return
    print("seq_id\tstart\tend\tlength\tframe\tstrand\tprotein")
    for o in all_orfs:
        print(
            f"{o['seq_id']}\t{o['start']}\t{o['end']}\t{o['length']}\t"
            f"{o['frame']}\t{o['strand']}\t{o['protein']}"
        )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("orf", help="Find open reading frames (ORFs)")
    p.add_argument("-fa", required=True, help="Input FASTA file")
    p.add_argument(
        "--min-len",
        type=int,
        default=100,
        help="Minimum ORF nucleotide length (default: 100)",
    )
    p.add_argument(
        "--all-frames",
        action="store_true",
        help="Search all 3 forward frames (default: frame 1 only)",
    )
    p.add_argument(
        "--top",
        type=int,
        default=0,
        help="Keep top N ORFs per sequence by length (0 = all)",
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
