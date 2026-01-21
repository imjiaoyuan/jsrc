import argparse

def extract_sequences(id_file, fasta_file, output_file):
    with open(id_file, 'r') as f:
        raw_ids = [line.strip() for line in f if line.strip()]
        target_ids = {rid.lower().split('.')[0]: rid for rid in raw_ids}
    
    found_records = {}
    
    with open(fasta_file, 'r') as infile:
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
    
    with open(output_file, 'w') as outfile:
        for lower_id in target_ids:
            if lower_id in found_records:
                record = found_records[lower_id]
                outfile.write('>' + record['header'] + '\n')
                outfile.write(record['seq'] + '\n')
    
    not_found = [target_ids[lid] for lid in target_ids if lid not in found_records]
    if not_found:
        print(f"Not found IDs ({len(not_found)}):", ', '.join(not_found))
    else:
        print("All sequences extracted successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-ids', required=True)
    parser.add_argument('-fa', required=True)
    parser.add_argument('-o', required=True)
    
    args = parser.parse_args()
    extract_sequences(args.ids, args.fa, args.o)