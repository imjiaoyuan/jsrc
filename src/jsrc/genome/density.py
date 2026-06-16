import json
import logging
from argparse import Namespace
from typing import Any

from Bio import SeqIO

logger = logging.getLogger(__name__)


def _calculate_density(
    features: list[tuple[int, int]], genome_length: int, window: int, step: int
) -> list[dict[str, Any]]:
    results = []
    for i in range(0, max(1, genome_length - window + 1), step):
        window_start = i
        window_end = i + window
        count = 0
        total_length = 0

        for start, end in features:
            overlap_start = max(window_start, start)
            overlap_end = min(window_end, end)
            if overlap_start < overlap_end:
                count += 1
                total_length += overlap_end - overlap_start

        density = count / (window / 1000)
        coverage = total_length / window if window > 0 else 0.0

        results.append(
            {
                "position": window_start,
                "count": count,
                "density": density,
                "coverage": coverage,
            }
        )

    return results


def cmd(args: Namespace) -> None:
    genome_lengths = {}
    for rec in SeqIO.parse(args.fa, "fasta"):
        genome_lengths[rec.id] = len(rec.seq)

    features_by_seq: dict[str, list[tuple[int, int]]] = {}
    with open(args.gff) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9:
                continue

            seq_id = parts[0]
            feature_type = parts[2]
            start = int(parts[3]) - 1
            end = int(parts[4])

            if args.feature_type and feature_type != args.feature_type:
                continue

            if seq_id not in features_by_seq:
                features_by_seq[seq_id] = []
            features_by_seq[seq_id].append((start, end))

    results = []
    for seq_id, length in genome_lengths.items():
        features = features_by_seq.get(seq_id, [])
        density_data = _calculate_density(features, length, args.window, args.step)
        results.append(
            {
                "seq_id": seq_id,
                "length": length,
                "total_features": len(features),
                "density": density_data,
            }
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    for item in results:
        logger.info(
            "seq_id\t%s\tlength\t%s\tfeatures\t%d",
            item["seq_id"],
            item["length"],
            item["total_features"],
        )
        if item["density"]:
            print(f"# {item['seq_id']}")
            print("position\tcount\tdensity\tcoverage")
            for d in item["density"]:
                print(
                    f"{d['position']}\t{d['count']}\t{d['density']:.4f}\t{d['coverage']:.4f}"
                )


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "density", help="Calculate gene/feature density along genome"
    )
    p.add_argument("-fa", required=True, help="Genome FASTA file")
    p.add_argument("-gff", required=True, help="GFF annotation file")
    p.add_argument("--feature-type", help="Feature type to count (e.g., gene, CDS)")
    p.add_argument("--window", type=int, default=10000, help="Window size")
    p.add_argument("--step", type=int, default=5000, help="Step size")
    p.add_argument("--json", action="store_true", help="Print JSON")
    p.set_defaults(func=cmd)
