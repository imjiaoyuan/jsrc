import json
from argparse import Namespace
from typing import Any

from Bio import SeqIO


def cmd(args: Namespace) -> None:
    try:
        import edlib
    except ImportError as err:
        raise SystemExit(
            "Error: edlib is required for genome comparison.\n"
            "Install with: pip install edlib"
        ) from err

    records1 = list(SeqIO.parse(args.fa1, "fasta"))
    records2 = list(SeqIO.parse(args.fa2, "fasta"))

    if not records1 or not records2:
        raise SystemExit("One or both FASTA files contain no sequences")

    genome1 = "".join(str(rec.seq).upper().replace("U", "T") for rec in records1)
    genome2 = "".join(str(rec.seq).upper().replace("U", "T") for rec in records2)

    print(f"Genome 1 ({args.fa1}): {len(genome1):,} bp")
    print(f"Genome 2 ({args.fa2}): {len(genome2):,} bp")
    print("\nPerforming global alignment (this may take a while)...")

    result = edlib.align(genome2, genome1, mode="NW", task="path")
    if result["editDistance"] == -1:
        raise SystemExit("Alignment failed")

    nice = edlib.getNiceAlignment(result, genome2, genome1)
    aln1 = nice["target_aligned"]
    aln2 = nice["query_aligned"]

    aln_len = len(aln1)
    matches = mismatches = ins1 = ins2 = 0
    for c1, c2 in zip(aln1, aln2, strict=True):
        if c1 == c2 and c1 != "-":
            matches += 1
        elif c1 != "-" and c2 != "-" and c1 != c2:
            mismatches += 1
        elif c1 == "-" and c2 != "-":
            ins1 += 1
        elif c1 != "-" and c2 == "-":
            ins2 += 1

    total_indels = ins1 + ins2
    percent_id = 100.0 * matches / aln_len if aln_len else 0.0

    stats = {
        "genome1": args.fa1,
        "genome2": args.fa2,
        "genome1_length": len(genome1),
        "genome2_length": len(genome2),
        "alignment_length": aln_len,
        "matches": matches,
        "mismatches": mismatches,
        "insertions_in_genome1": ins1,
        "insertions_in_genome2": ins2,
        "total_indels": total_indels,
        "percent_identity": round(percent_id, 4),
        "edit_distance": result["editDistance"],
    }

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    print("\n" + "=" * 50)
    print("GENOME COMPARISON STATISTICS")
    print("=" * 50)
    print(f"{'Alignment length':40} : {stats['alignment_length']:>15,} bp")
    print(f"{'Matches':40} : {stats['matches']:>15,}")
    print(f"{'Mismatches (substitutions)':40} : {stats['mismatches']:>15,}")
    print(
        f"{'Insertions in genome1 (gaps in genome2)':40} : {stats['insertions_in_genome1']:>15,}"
    )
    print(
        f"{'Insertions in genome2 (gaps in genome1)':40} : {stats['insertions_in_genome2']:>15,}"
    )
    print(f"{'Total indels':40} : {stats['total_indels']:>15,}")
    print(f"{'Percent identity':40} : {stats['percent_identity']:>14.4f}%")
    print(f"{'Edit distance (Levenshtein)':40} : {stats['edit_distance']:>15,}")
    print("=" * 50)


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "compare",
        help="Genome-wide alignment and difference statistics (requires edlib)",
    )
    p.add_argument("-fa1", required=True, help="First genome FASTA file")
    p.add_argument("-fa2", required=True, help="Second genome FASTA file")
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
