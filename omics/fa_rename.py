import sys
import argparse
import csv
from Bio import SeqIO

def rename_fasta_ids(fasta_file, id_map_file, output_file):
    id_map = {}
    not_renamed = []
    
    with open(id_map_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                old_id, new_id = row[0], row[1]
                id_map[old_id] = new_id
    
    with open(fasta_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for record in SeqIO.parse(f_in, 'fasta'):
            old_id = record.id
            if old_id in id_map:
                record.id = id_map[old_id]
                record.description = ''
            else:
                not_renamed.append(old_id)
            
            SeqIO.write(record, f_out, 'fasta')
    
    if not_renamed:
        print(f"Genes not renamed: {len(not_renamed)}")
        for gene in not_renamed:
            print(gene)
    else:
        print("All genes renamed successfully.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rename FASTA sequence IDs')
    parser.add_argument('-fa', '--fasta', required=True, help='Input FASTA file')
    parser.add_argument('-id', '--id_map', required=True, help='ID mapping CSV file')
    parser.add_argument('-o', '--output', required=True, help='Output FASTA file')
    
    args = parser.parse_args()
    
    rename_fasta_ids(args.fasta, args.id_map, args.output)