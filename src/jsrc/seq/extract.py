from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.common.gff import parse_gff_attributes


def _load_target_ids(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _merge_regions(regions: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not regions:
        return []
    regions = sorted(regions)
    merged = [regions[0]]
    for start, end in regions[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def cmd(args):
    if not args.feature.strip():
        raise SystemExit("-feature must be a non-empty string")
    if not args.match.strip():
        raise SystemExit("-match must be a non-empty string")
    targets = _load_target_ids(args.ids)
    if not targets:
        raise SystemExit("No target IDs found in -ids file")
    target_set = set(targets)
    grouped: dict[str, list[tuple[str, int, int, str]]] = {tid: [] for tid in targets}

    with open(args.gff, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9 or parts[2] != args.feature:
                continue
            chrom = parts[0]
            start = int(parts[3]) - 1
            end = int(parts[4])
            strand = parts[6]
            attrs = parse_gff_attributes(parts[8])
            raw = attrs.get(args.match)
            if not raw:
                continue
            matched = [x.strip() for x in raw.split(",") if x.strip()]
            for key in matched:
                if key in target_set:
                    grouped[key].append((chrom, start, end, strand))

    genome = SeqIO.index(args.fa, "fasta")
    try:
        extracted = 0
        with open(args.o, "w", encoding="utf-8") as out_fh:
            for tid in targets:
                segments = grouped.get(tid, [])
                if not segments:
                    continue
                by_locus: dict[tuple[str, str], list[tuple[int, int]]] = {}
                for chrom, start, end, strand in segments:
                    by_locus.setdefault((chrom, strand), []).append((start, end))
                best_locus = max(
                    by_locus.items(), key=lambda item: sum(e - s for s, e in item[1])
                )
                (chrom, strand), regions = best_locus
                regions = _merge_regions(regions)
                if chrom not in genome:
                    continue
                chrom_seq = genome[chrom].seq
                seq = Seq("")
                for start, end in regions:
                    seq += chrom_seq[start:end]
                if strand == "-":
                    seq = seq.reverse_complement()
                desc = f"feature={args.feature};match={args.match};locus={chrom};strand={strand}"
                record = SeqRecord(Seq(str(seq)), id=tid, description=desc)
                SeqIO.write(record, out_fh, "fasta")
                extracted += 1
    finally:
        genome.close()

    print(f"Extracted {extracted}/{len(targets)} sequences to {args.o}")
