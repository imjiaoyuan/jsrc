from __future__ import annotations

import json
import math
from argparse import Namespace
from collections import Counter
from typing import Any

from jsrc.core import ValidationError, load_fasta
from jsrc.genome.core import normalize_sequence


def _kmer_profile(seq: str, k: int) -> Counter:
    seq = normalize_sequence(seq)
    kmers: Counter[str] = Counter()
    valid_bases = set("ACGT")
    for i in range(len(seq) - k + 1):
        kmer = seq[i : i + k]
        if all(b in valid_bases for b in kmer):
            kmers[kmer] += 1
    return kmers


def _jaccard_similarity(profile1: Counter, profile2: Counter) -> float:
    all_kmers = set(profile1.keys()) | set(profile2.keys())
    if not all_kmers:
        return 0.0
    intersection = sum(min(profile1[k], profile2[k]) for k in all_kmers)
    union = sum(max(profile1[k], profile2[k]) for k in all_kmers)
    return intersection / union if union > 0 else 0.0


def _cosine_similarity(profile1: Counter, profile2: Counter) -> float:
    all_kmers = set(profile1.keys()) | set(profile2.keys())
    if not all_kmers:
        return 0.0
    dot = sum(profile1[k] * profile2[k] for k in all_kmers)
    norm1 = math.sqrt(sum(v * v for v in profile1.values()))
    norm2 = math.sqrt(sum(v * v for v in profile2.values()))
    return dot / (norm1 * norm2) if norm1 > 0 and norm2 > 0 else 0.0


def _mash_distance(profile1: Counter, profile2: Counter, k: int) -> float:
    jaccard = _jaccard_similarity(profile1, profile2)
    if jaccard == 0:
        return 1.0
    return -1.0 / k * math.log(2.0 * jaccard / (1.0 + jaccard))


def cmd(args: Namespace) -> None:
    if args.k < 1:
        raise ValidationError("-k must be >= 1")

    records1 = load_fasta(args.fa1)
    records2 = load_fasta(args.fa2)

    seq1 = "".join(str(rec.seq) for rec in records1)
    seq2 = "".join(str(rec.seq) for rec in records2)

    profile1 = _kmer_profile(seq1, args.k)
    profile2 = _kmer_profile(seq2, args.k)

    jaccard = _jaccard_similarity(profile1, profile2)
    cosine = _cosine_similarity(profile1, profile2)
    mash_dist = _mash_distance(profile1, profile2, args.k)
    ani_estimate = (1.0 - mash_dist) * 100.0

    result = {
        "genome1": args.fa1,
        "genome2": args.fa2,
        "k": args.k,
        "genome1_length": len(seq1),
        "genome2_length": len(seq2),
        "genome1_kmers": sum(profile1.values()),
        "genome2_kmers": sum(profile2.values()),
        "shared_kmers": len(set(profile1.keys()) & set(profile2.keys())),
        "jaccard_similarity": round(jaccard, 6),
        "cosine_similarity": round(cosine, 6),
        "mash_distance": round(mash_dist, 6),
        "ani_estimate_percent": round(ani_estimate, 4),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"{'Genome 1':30} : {result['genome1']}")
    print(f"{'Genome 2':30} : {result['genome2']}")
    print(f"{'k-mer size':30} : {result['k']}")
    print(f"{'Genome 1 length (bp)':30} : {result['genome1_length']:,}")
    print(f"{'Genome 2 length (bp)':30} : {result['genome2_length']:,}")
    print(f"{'Genome 1 k-mers':30} : {result['genome1_kmers']:,}")
    print(f"{'Genome 2 k-mers':30} : {result['genome2_kmers']:,}")
    print(f"{'Shared k-mers':30} : {result['shared_kmers']:,}")
    print(f"{'Jaccard similarity':30} : {result['jaccard_similarity']:.6f}")
    print(f"{'Cosine similarity':30} : {result['cosine_similarity']:.6f}")
    print(f"{'Mash distance':30} : {result['mash_distance']:.6f}")
    print(f"{'ANI estimate (%)':30} : {result['ani_estimate_percent']:.4f}")


def register(subparsers: Any) -> None:
    p = subparsers.add_parser(
        "ani", help="Average Nucleotide Identity estimation (k-mer based)"
    )
    p.add_argument("-fa1", required=True, help="First genome FASTA file")
    p.add_argument("-fa2", required=True, help="Second genome FASTA file")
    p.add_argument("-k", type=int, default=21, help="k-mer size (default: 21)")
    p.add_argument("--json", action="store_true", help="Print JSON output")
    p.set_defaults(func=cmd)
