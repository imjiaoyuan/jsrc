import argparse
import re
import sys
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fa', required=True)
    parser.add_argument('-gff', required=True)
    parser.add_argument('-id', required=True)
    parser.add_argument('-o', required=True)
    parser.add_argument('-oc', required=True)
    args = parser.parse_args()

    cds_coords = {}
    strand_map = {}

    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9 or parts[2] != 'CDS':
                continue
            
            attr = parts[8]
            pattern = re.compile(rf'{args.id}[\s=]+"?([^";\s]+)"?')
            match = pattern.search(attr)
            
            if match:
                seq_id = match.group(1)
                chrom = parts[0]
                try:
                    start = int(parts[3])
                    end = int(parts[4])
                except ValueError:
                    continue
                strand = parts[6]
                
                if seq_id not in cds_coords:
                    cds_coords[seq_id] = []
                    strand_map[seq_id] = strand
                
                cds_coords[seq_id].append((chrom, start, end))

    genome = SeqIO.index(args.fa, "fasta")
    
    prot_records = []
    cds_records = []

    for seq_id, exons in cds_coords.items():
        exons.sort(key=lambda x: x[1])
        chrom = exons[0][0]
        
        rec = None
        if chrom in genome:
            rec = genome[chrom]
        elif chrom.startswith('chr') and chrom[3:] in genome:
            rec = genome[chrom[3:]]
        elif ('chr' + chrom) in genome:
            rec = genome['chr' + chrom]
            
        if not rec:
            continue
            
        seq_obj = Seq("")
        for c, s, e in exons:
            if c != chrom:
                continue
            seq_obj += rec.seq[s-1:e]
            
        if strand_map[seq_id] == '-':
            seq_obj = seq_obj.reverse_complement()
            
        cds_record = SeqRecord(seq_obj, id=seq_id, description="")
        cds_records.append(cds_record)
        
        try:
            prot_seq = seq_obj.translate(to_stop=True)
            prot_record = SeqRecord(prot_seq, id=seq_id, description="")
            prot_records.append(prot_record)
        except Exception:
            pass

    SeqIO.write(cds_records, args.oc, "fasta")
    SeqIO.write(prot_records, args.o, "fasta")

if __name__ == "__main__":
    main()