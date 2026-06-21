import logging
from argparse import Namespace
from pathlib import Path
from typing import Any

from Bio import SeqIO

from jsrc.core import ValidationError

logger = logging.getLogger(__name__)


def cmd(args: Namespace) -> None:
    in_path = Path(args.input)
    if not in_path.exists():
        raise ValidationError(f"Input file not found: {args.input}")
    out_path = Path(args.o)

    count = SeqIO.convert(str(in_path), args.from_fmt, str(out_path), args.to_fmt)
    logger.info(
        "Converted %d records from %s → %s: %s", count, args.from_fmt, args.to_fmt, out_path
    )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("convert", help="Convert between sequence file formats")
    p.add_argument("-i", "--input", required=True, help="Input file")
    p.add_argument("--from", dest="from_fmt", required=True, help="Source format")
    p.add_argument("--to", dest="to_fmt", required=True, help="Target format")
    p.add_argument("-o", required=True, help="Output file")
    p.set_defaults(func=cmd)
