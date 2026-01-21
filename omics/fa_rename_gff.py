import argparse
import sys
import re
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fa', required=True)
    parser.add_argument('-gff', required=True)
    parser.add_argument('-parent', required=True)
    parser.add_argument('-o', required=True)
    args = parser.parse_args()

    target_ids = set()
    for rec in SeqIO.parse(args.fa, "fasta"):
        target_ids.add(rec.id)

    id_map = {}
    
    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
            
            attr_str = parts[8]
            attrs = {}
            
            items = attr_str.strip().split(';')
            for item in items:
                item = item.strip()
                if not item:
                    continue
                
                if '=' in item:
                    k, v = item.split('=', 1)
                    attrs[k.strip()] = v.strip().replace('"', '')
                else:
                    m = re.match(r'^([^\s]+)\s+(.+)$', item)
                    if m:
                        k = m.group(1).strip()
                        v = m.group(2).strip().replace('"', '')
                        attrs[k] = v
            
            if args.parent in attrs:
                parent_val = attrs[args.parent]
                for k, v in attrs.items():
                    if v in target_ids:
                        id_map[v] = parent_val

    converted_count = 0
    failed_ids = []

    with open(args.o, 'w') as out_f:
        for rec in SeqIO.parse(args.fa, "fasta"):
            if rec.id in id_map:
                new_id = id_map[rec.id]
                new_rec = SeqRecord(rec.seq, id=new_id, description="")
                SeqIO.write(new_rec, out_f, "fasta")
                converted_count += 1
            else:
                new_rec = SeqRecord(rec.seq, id=rec.id, description="")
                SeqIO.write(new_rec, out_f, "fasta")
                failed_ids.append(rec.id)

    print(f"Total sequences: {len(target_ids)}")
    print(f"Converted: {converted_count}")
    print(f"Failed to convert: {len(failed_ids)}")
    
    if failed_ids:
        print("Failed IDs:")
        for fid in failed_ids:
            print(fid)

if __name__ == "__main__":
    main()