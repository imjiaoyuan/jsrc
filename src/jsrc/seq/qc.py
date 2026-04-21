import gzip
import json

from Bio import SeqIO


def _open_text(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def _nxx(lengths: list[int], pct: float) -> int:
    if not lengths:
        return 0
    target = sum(lengths) * pct
    acc = 0
    for x in sorted(lengths, reverse=True):
        acc += x
        if acc >= target:
            return x
    return 0


def _fasta_stats(path: str) -> dict[str, float | int]:
    lengths = []
    gc = 0
    acgt = 0
    n_bases = 0
    for rec in SeqIO.parse(path, "fasta"):
        seq = str(rec.seq).upper()
        lengths.append(len(seq))
        gc += seq.count("G") + seq.count("C")
        acgt += seq.count("A") + seq.count("C") + seq.count("G") + seq.count("T")
        n_bases += seq.count("N")
    total = sum(lengths)
    return {
        "sequence_count": len(lengths),
        "total_bases": total,
        "max_len": max(lengths) if lengths else 0,
        "min_len": min(lengths) if lengths else 0,
        "n50": _nxx(lengths, 0.5),
        "n90": _nxx(lengths, 0.9),
        "gc_percent": (gc / acgt * 100.0) if acgt else 0.0,
        "n_percent": (n_bases / total * 100.0) if total else 0.0,
    }


def _fastq_stats(paths: list[str], genome_size: int | None) -> dict[str, float | int]:
    reads = 0
    bases = 0
    for path in paths:
        with _open_text(path) as f:
            line_no = 0
            for line in f:
                line_no += 1
                if line_no % 4 == 2:
                    reads += 1
                    bases += len(line.strip())
    out: dict[str, float | int] = {
        "reads": reads,
        "bases": bases,
        "mean_read_length": (bases / reads) if reads else 0.0,
    }
    if genome_size:
        out["estimated_depth"] = bases / genome_size
    return out


def _print_kv(section: str, data: dict[str, float | int]):
    print(f"[{section}]")
    for key, val in data.items():
        if isinstance(val, int):
            print(f"{key}\t{val:,}")
        else:
            print(f"{key}\t{val:.4f}")
    print("")


def cmd(args):
    if not args.fa and not args.fq:
        raise SystemExit("Need at least one input: -fa and/or -fq")
    out: dict[str, dict[str, float | int]] = {}
    if args.fa:
        out["fasta"] = _fasta_stats(args.fa)
    if args.fq:
        out["fastq"] = _fastq_stats(args.fq, args.gs)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    for section, stats in out.items():
        _print_kv(section, stats)
