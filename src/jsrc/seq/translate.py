import sys

from Bio import SeqIO
from Bio.Data.CodonTable import TranslationError
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from jsrc.common.gff import parse_gff_attributes


def cmd(args):
    genome = SeqIO.to_dict(SeqIO.parse(args.fa, "fasta"))
    cds_dict = {}

    with open(args.gff, "r", encoding="utf-8") as f:
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
        try:
            protein_seq = cds_seq.translate(to_stop=True)
            if len(protein_seq) > 0:
                proteins.append(SeqRecord(protein_seq, id=gene_id, description=""))
        except (TranslationError, ValueError) as exc:
            print(f"Warning: Failed to translate {gene_id}: {exc}", file=sys.stderr)
    SeqIO.write(proteins, args.o, "fasta")
    print(f"Translated {len(proteins)} genes to {args.o}")
