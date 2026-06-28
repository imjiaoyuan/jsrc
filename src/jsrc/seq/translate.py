from __future__ import annotations

import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO
from Bio.Data.CodonTable import TranslationError
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.core import open_text, parse_gff_attributes

logger = logging.getLogger(__name__)


def cmd(args: Namespace) -> None:
    genome = SeqIO.to_dict(SeqIO.parse(args.fa, "fasta"))
    cds_dict: dict[str, dict[str, Any]] = {}

    with open_text(args.gff) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9 or parts[2] != "CDS":
                continue
            chrom = parts[0]
            start = int(parts[3]) - 1
            end = int(parts[4])
            strand = parts[6]
            attr = parse_gff_attributes(parts[8])
            gene_id = attr.get(args.id)
            if not gene_id or chrom not in genome:
                continue
            cds_dict.setdefault(
                gene_id, {"chrom": chrom, "strand": strand, "regions": []}
            )
            cds_dict[gene_id]["regions"].append((start, end))

    proteins = []
    for gene_id, data in cds_dict.items():
        chrom_seq = genome[data["chrom"]].seq
        regions = sorted(data["regions"])
        cds_seq = Seq("")
        for start, end in regions:
            cds_seq += chrom_seq[start:end]
        if data["strand"] == "-":
            cds_seq = cds_seq.reverse_complement()
        remainder = len(cds_seq) % 3
        if remainder:
            logger.warning(
                "CDS length for %s is not divisible by 3; trimming %d nt",
                gene_id,
                remainder,
            )
            cds_seq = cds_seq[:-remainder]
        if len(cds_seq) == 0:
            logger.error("Failed to translate %s: empty CDS after trimming", gene_id)
            continue
        try:
            protein_seq = cds_seq.translate(to_stop=True)
            if len(protein_seq) > 0:
                proteins.append(SeqRecord(protein_seq, id=gene_id, description=""))
        except (TranslationError, ValueError):
            logger.exception("Failed to translate %s", gene_id)
    SeqIO.write(proteins, args.o, "fasta")
    logger.info("Translated %d genes to %s", len(proteins), args.o)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser("translate", help="Extract CDS and translate to protein")
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("-id", required=True, help="Gene ID field in GFF")
    p.add_argument("-o", required=True, help="Output protein FASTA")
    p.set_defaults(func=cmd)
