from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.common.gff import parse_gff_attributes


def _read_target_ids(path: str) -> set[str]:
    with open(path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def cmd(args):
    if args.up < 0 or args.down < 0:
        raise SystemExit("-up and -down must be non-negative.")
    genome = SeqIO.to_dict(SeqIO.parse(args.fa, "fasta"))
    targets = _read_target_ids(args.ids)
    promoters: list[SeqRecord] = []

    with open(args.gff, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 9 or parts[2] != args.feature:
                continue
            chrom = parts[0]
            start = int(parts[3])
            end = int(parts[4])
            strand = parts[6]
            attr = parse_gff_attributes(parts[8])
            gene_id = attr.get(args.id)
            if not gene_id or gene_id not in targets or chrom not in genome:
                continue

            chrom_seq = genome[chrom].seq
            chrom_len = len(chrom_seq)
            if strand == "+":
                p_start = max(0, (start - 1) - args.up)
                p_end = min(chrom_len, (start - 1) + args.down)
                seq = chrom_seq[p_start:p_end]
            else:
                p_start = max(0, end - args.down)
                p_end = min(chrom_len, end + args.up)
                seq = chrom_seq[p_start:p_end].reverse_complement()

            if len(seq) == 0:
                continue
            desc = f"{chrom}:{p_start + 1}-{p_end}({strand}) up={args.up} down={args.down}"
            promoters.append(SeqRecord(Seq(str(seq)), id=gene_id, description=desc))

    SeqIO.write(promoters, args.o, "fasta")
    print(f"Extracted {len(promoters)} promoter sequences to {args.o}")
