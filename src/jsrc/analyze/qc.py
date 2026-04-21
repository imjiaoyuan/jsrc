import gzip
import json
import re

from Bio import SeqIO


def _open_text(path: str):
    if path.endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def _format_int(x: int) -> str:
    return f"{x:,}"


def _format_float(x: float, ndigits: int = 2) -> str:
    return f"{x:.{ndigits}f}"


def _nxx(lengths: list[int], pct: float) -> int:
    if not lengths:
        return 0
    target = sum(lengths) * pct
    acc = 0
    for v in sorted(lengths, reverse=True):
        acc += v
        if acc >= target:
            return v
    return 0


def _assembly_stats(fasta_path: str) -> dict[str, float | int]:
    lengths: list[int] = []
    gc = 0
    acgt = 0
    n_bases = 0
    for rec in SeqIO.parse(fasta_path, "fasta"):
        seq = str(rec.seq).upper()
        lengths.append(len(seq))
        gc += seq.count("G") + seq.count("C")
        acgt += seq.count("A") + seq.count("C") + seq.count("G") + seq.count("T")
        n_bases += seq.count("N")
    total_len = sum(lengths)
    return {
        "contig_count": len(lengths),
        "total_bases": total_len,
        "max_contig": max(lengths) if lengths else 0,
        "min_contig": min(lengths) if lengths else 0,
        "n50": _nxx(lengths, 0.5),
        "n90": _nxx(lengths, 0.9),
        "gc_percent": (gc / acgt * 100.0) if acgt else 0.0,
        "n_percent": (n_bases / total_len * 100.0) if total_len else 0.0,
    }


_CIGAR_RE = re.compile(r"(\d+)([MIDNSHP=X])")


def _mapped_ref_bases(cigar: str) -> int:
    # Reference-consuming ops: M, D, N, =, X
    total = 0
    for length, op in _CIGAR_RE.findall(cigar):
        if op in {"M", "D", "N", "=", "X"}:
            total += int(length)
    return total


def _sam_stats(sam_path: str) -> dict[str, float | int]:
    total = 0
    mapped = 0
    covered_ref_bases = 0
    ref_len = 0
    with _open_text(sam_path) as f:
        for line in f:
            if line.startswith("@SQ"):
                fields = line.rstrip("\n").split("\t")
                for field in fields:
                    if field.startswith("LN:"):
                        ref_len += int(field[3:])
                continue
            if line.startswith("@"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 6:
                continue
            total += 1
            flag = int(parts[1])
            is_mapped = (flag & 4) == 0
            if is_mapped:
                mapped += 1
                covered_ref_bases += _mapped_ref_bases(parts[5])
    mapping_rate = (mapped / total * 100.0) if total else 0.0
    depth = (covered_ref_bases / ref_len) if ref_len else 0.0
    return {
        "total_alignments": total,
        "mapped_alignments": mapped,
        "mapping_rate_percent": mapping_rate,
        "reference_total_bases": ref_len,
        "mapped_reference_bases": covered_ref_bases,
        "mean_depth_from_sam": depth,
    }


def _fastq_stats(paths: list[str], genome_size: int | None) -> dict[str, float | int]:
    reads = 0
    bases = 0
    for path in paths:
        with _open_text(path) as f:
            i = 0
            for line in f:
                i += 1
                if i % 4 == 2:
                    reads += 1
                    bases += len(line.strip())
    out: dict[str, float | int] = {
        "reads": reads,
        "bases": bases,
        "mean_read_length": (bases / reads) if reads else 0.0,
    }
    if genome_size:
        out["estimated_depth_from_fastq"] = bases / genome_size
    return out


def _vcf_stats(vcf_path: str) -> dict[str, int]:
    total = 0
    snp = 0
    indel = 0
    other = 0
    with _open_text(vcf_path) as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 5:
                continue
            total += 1
            ref = parts[3]
            alts = [x for x in parts[4].split(",") if x]
            if not alts:
                other += 1
                continue
            if all(a.startswith("<") and a.endswith(">") for a in alts):
                other += 1
                continue
            if len(ref) == 1 and all(len(a) == 1 for a in alts):
                snp += 1
            elif any(len(a) != len(ref) for a in alts):
                indel += 1
            else:
                other += 1
    return {
        "variant_total": total,
        "snp_count": snp,
        "indel_count": indel,
        "other_variant_count": other,
    }


def _print_human(stats: dict[str, dict[str, float | int]]) -> None:
    for section, values in stats.items():
        print(f"[{section}]")
        for k, v in values.items():
            if isinstance(v, int):
                val = _format_int(v)
            else:
                if abs(v) >= 100:
                    val = _format_float(v, 2)
                else:
                    val = _format_float(v, 4)
            print(f"{k}\t{val}")
        print("")


def cmd(args):
    if not any([args.fa, args.sam, args.vcf, args.fq]):
        raise SystemExit("At least one input is required: -fa and/or -sam and/or -vcf and/or -fq")

    stats: dict[str, dict[str, float | int]] = {}
    if args.fa:
        stats["assembly"] = _assembly_stats(args.fa)
    if args.sam:
        stats["mapping"] = _sam_stats(args.sam)
    if args.fq:
        stats["fastq"] = _fastq_stats(args.fq, args.gs)
    if args.vcf:
        stats["variants"] = _vcf_stats(args.vcf)

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    _print_human(stats)
