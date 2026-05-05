import json
import logging
import sys
from argparse import Namespace
from typing import Any

from Bio import Entrez, SeqIO

logger = logging.getLogger(__name__)


def _parse_ids(raw: list[str]) -> list[str]:
    """Parse accession IDs from command-line arguments.

    Each item is treated as a literal ID unless it refers to an existing
    file, in which case whitespace-stripped non-empty lines are read.
    """
    ids: list[str] = []
    for item in raw:
        try:
            with open(item, "r", encoding="utf-8") as fh:
                content = [line.strip() for line in fh if line.strip()]
                if content:
                    ids.extend(content)
                    continue
        except OSError:
            pass
        ids.append(item)
    return ids


def cmd(args: Namespace) -> None:
    Entrez.email = args.email

    ids = _parse_ids(args.ids)
    if not ids:
        raise SystemExit("No accession IDs provided")

    id_str = ",".join(ids)
    if args.format == "genbank":
        rettype = "gb"
        parse_fmt = "genbank"
    else:
        rettype = "fasta"
        parse_fmt = "fasta"

    logger.info("Fetching %d record(s) from NCBI %s", len(ids), args.db)
    try:
        handle = Entrez.efetch(db=args.db, id=id_str, rettype=rettype, retmode="text")
        records = list(SeqIO.parse(handle, parse_fmt))
        handle.close()
    except Exception as exc:
        raise SystemExit(f"Entrez fetch failed: {exc}")

    if not records:
        raise SystemExit("No records returned from NCBI")

    if args.o:
        SeqIO.write(records, args.o, parse_fmt)
        logger.info("Wrote %d record(s) to %s", len(records), args.o)
    elif not args.json:
        SeqIO.write(records, sys.stdout, parse_fmt)

    if args.json:
        summary = [
            {
                "id": rec.id,
                "name": rec.name,
                "description": rec.description,
                "length": len(rec.seq),
            }
            for rec in records
        ]
        print(json.dumps(summary, indent=2))


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("fetch", help="Fetch sequences from NCBI via Entrez")
    p.add_argument(
        "-ids",
        nargs="+",
        required=True,
        help="Accession IDs or file containing IDs",
    )
    p.add_argument("-o", help="Output file (default: stdout)")
    p.add_argument(
        "--format",
        choices=["fasta", "genbank"],
        default="fasta",
        help="Output format",
    )
    p.add_argument(
        "-db", default="nucleotide", help="NCBI database (default: nucleotide)"
    )
    p.add_argument("--email", required=True, help="Email for NCBI Entrez (required)")
    p.add_argument("--json", action="store_true", help="Print JSON summary")
    p.set_defaults(func=cmd)
