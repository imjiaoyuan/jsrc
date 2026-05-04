import sys
import csv
import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def cmd_extract(args):
    with open(args.ids, 'r') as f:
        raw_ids = [line.strip() for line in f if line.strip()]
        target_ids = {rid.lower().split('.')[0]: rid for rid in raw_ids}
    
    found_records = {}
    
    with open(args.fa, 'r') as infile:
        current_header = None
        current_seq_lines = []
        
        def save_record(header, seq_lines):
            if not header:
                return
            full_header = header[1:]
            first_word = full_header.split()[0]
            
            clean_id = first_word.lower().split('.')[0]
            seq = ''.join(seq_lines)
            
            if clean_id in target_ids:
                if clean_id not in found_records or len(seq) > len(found_records[clean_id]['seq']):
                    found_records[clean_id] = {
                        'header': target_ids[clean_id],
                        'seq': seq
                    }
        
        for line in infile:
            line = line.strip()
            if not line:
                continue
            if line.startswith('>'):
                save_record(current_header, current_seq_lines)
                current_header = line
                current_seq_lines = []
            else:
                current_seq_lines.append(line)
        
        save_record(current_header, current_seq_lines)
    
    with open(args.o, 'w') as outfile:
        for clean_id in target_ids:
            if clean_id in found_records:
                rec = found_records[clean_id]
                outfile.write(f">{rec['header']}\n{rec['seq']}\n")
    
    print(f"Extracted {len(found_records)}/{len(target_ids)} sequences to {args.o}")

def cmd_rename(args):
    mapping = {}
    with open(args.map, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2:
                mapping[row[0].strip()] = row[1].strip()
    
    with open(args.fa, 'r') as fin, open(args.o, 'w') as fout:
        for line in fin:
            if line.startswith('>'):
                old_id = line[1:].split()[0]
                if old_id in mapping:
                    fout.write(f">{mapping[old_id]}\n")
                else:
                    fout.write(line)
            else:
                fout.write(line)
    
    print(f"Renamed {len(mapping)} sequences to {args.o}")

def cmd_rename_by_gff(args):
    from common import parse_gff_attributes
    
    mapping = {}
    
    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue
            
            if parts[2] == 'mRNA':
                attr = parse_gff_attributes(parts[8])
                tid = attr.get('ID')
                pid = attr.get(args.parent)
                if tid and pid:
                    mapping[tid] = pid
    
    with open(args.fa, 'r') as fin, open(args.o, 'w') as fout:
        for line in fin:
            if line.startswith('>'):
                old_id = line[1:].split()[0]
                if old_id in mapping:
                    fout.write(f">{mapping[old_id]}\n")
                else:
                    fout.write(line)
            else:
                fout.write(line)
    
    print(f"Renamed {len(mapping)} transcripts to {args.o}")

def cmd_translate(args):
    from common import parse_gff_attributes
    
    genome = SeqIO.to_dict(SeqIO.parse(args.fa, 'fasta'))
    
    cds_dict = {}
    
    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9 or parts[2] != 'CDS':
                continue
            
            chrom = parts[0]
            start = int(parts[3]) - 1
            end = int(parts[4])
            strand = parts[6]
            
            attr = parse_gff_attributes(parts[8])
            gene_id = attr.get(args.id)
            
            if not gene_id or chrom not in genome:
                continue
            
            if gene_id not in cds_dict:
                cds_dict[gene_id] = {'chrom': chrom, 'strand': strand, 'regions': []}
            
            cds_dict[gene_id]['regions'].append((start, end))
    
    proteins = []
    
    for gene_id, data in cds_dict.items():
        chrom_seq = genome[data['chrom']].seq
        
        regions = sorted(data['regions'])
        cds_seq = Seq('')
        for start, end in regions:
            cds_seq += chrom_seq[start:end]
        
        if data['strand'] == '-':
            cds_seq = cds_seq.reverse_complement()
        
        try:
            protein_seq = cds_seq.translate(to_stop=True)
            if len(protein_seq) > 0:
                proteins.append(SeqRecord(protein_seq, id=gene_id, description=''))
        except Exception as e:
            print(f"Warning: Failed to translate {gene_id}: {e}", file=sys.stderr)
            continue
    
    SeqIO.write(proteins, args.o, 'fasta')
    print(f"Translated {len(proteins)} genes to {args.o}")
