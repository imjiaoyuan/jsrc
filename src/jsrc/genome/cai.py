import json
import logging
from argparse import Namespace
from collections import Counter
from typing import Any

from Bio import SeqIO

from jsrc.core import DataFormatError
from jsrc.genome.core import (
    AA_TABLE,
    calculate_cai,
    iter_codons,
    make_aa_to_codons,
)

logger = logging.getLogger(__name__)


def cmd(args: Namespace) -> None:
    aa_to_codons = make_aa_to_codons(AA_TABLE)

    ref_counts: Counter[str] = Counter()
    ref_records = list(SeqIO.parse(args.reference, "fasta"))
    if not ref_records:
        raise DataFormatError("No sequences found in reference FASTA")
    for rec in ref_records:
        for codon in iter_codons(str(rec.seq)):
            if AA_TABLE.get(codon) != "*":
                ref_counts[codon] += 1
    if not ref_counts:
        raise DataFormatError("No valid codons found in reference FASTA")
    logger.info(
        "Reference: %d sequences, %d codons",
        len(ref_records),
        sum(ref_counts.values()),
    )

    query_records = list(SeqIO.parse(args.fa, "fasta"))
    if not query_records:
        raise DataFormatError("No sequences found in query FASTA")

    results = []
    for rec in query_records:
        gene_counts: Counter[str] = Counter()
        for codon in iter_codons(str(rec.seq)):
            if AA_TABLE.get(codon) != "*":
                gene_counts[codon] += 1
        cai = calculate_cai(gene_counts, ref_counts, aa_to_codons)
        results.append(
            {
                "id": rec.id,
                "codon_count": sum(gene_counts.values()),
                "cai": round(cai, 6),
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print("id\tcodon_count\tcai")
    for r in results:
        print(f"{r['id']}\t{r['codon_count']}\t{r['cai']:.6f}")
    logger.info("Computed CAI for %d genes", len(results))


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "cai", help="Codon Adaptation Index for each gene"
    )
    p.add_argument("-fa", required=True, help="Query CDS FASTA file")
    p.add_argument(
        "--reference",
        required=True,
        help="Reference CDS FASTA file (highly expressed genes)",
    )
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
