import json
import logging
import re
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _scan_motif(seq: str, motif: str, allow_mismatch: int = 0) -> list[dict[str, Any]]:
    seq = seq.upper()
    motif = motif.upper()
    matches = []

    iupac_codes = {
        "R": "[AG]",
        "Y": "[CT]",
        "S": "[GC]",
        "W": "[AT]",
        "K": "[GT]",
        "M": "[AC]",
        "B": "[CGT]",
        "D": "[AGT]",
        "H": "[ACT]",
        "V": "[ACG]",
        "N": "[ACGT]",
    }

    regex_pattern = motif
    for code, pattern in iupac_codes.items():
        regex_pattern = regex_pattern.replace(code, pattern)

    if allow_mismatch == 0:
        for match in re.finditer(regex_pattern, seq):
            matches.append(
                {
                    "start": match.start(),
                    "end": match.end(),
                    "sequence": match.group(),
                    "mismatches": 0,
                }
            )
    else:
        motif_len = len(motif)
        for i in range(len(seq) - motif_len + 1):
            subseq = seq[i : i + motif_len]
            mismatches = 0
            for m_char, s_char in zip(motif, subseq, strict=True):
                if m_char in iupac_codes:
                    if not re.match(iupac_codes[m_char], s_char):
                        mismatches += 1
                elif m_char != s_char:
                    mismatches += 1

            if mismatches <= allow_mismatch:
                matches.append(
                    {
                        "start": i,
                        "end": i + motif_len,
                        "sequence": subseq,
                        "mismatches": mismatches,
                    }
                )

    return matches


def cmd(args: Namespace) -> None:
    results = []
    for rec in SeqIO.parse(args.fa, "fasta"):
        matches = _scan_motif(str(rec.seq), args.motif, args.mismatch)
        results.append(
            {
                "seq_id": rec.id,
                "length": len(rec.seq),
                "matches": matches,
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for item in results:
        logger.info(
            "seq_id\t%s\tlength\t%s\tmatches\t%d",
            item["seq_id"],
            item["length"],
            len(item["matches"]),
        )
        if item["matches"]:
            print(f"# {item['seq_id']}")
            print("start\tend\tsequence\tmismatches")
            for match in item["matches"][: args.top]:
                print(
                    f"{match['start']}\t{match['end']}\t{match['sequence']}\t{match['mismatches']}"
                )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "motif-scan", help="Scan for DNA motifs (supports IUPAC codes)"
    )
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument(
        "-m", "--motif", required=True, help="Motif pattern (IUPAC codes supported)"
    )
    p.add_argument("--mismatch", type=int, default=0, help="Allow N mismatches")
    p.add_argument(
        "--top", type=int, default=100, help="Show top N matches per sequence"
    )
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
