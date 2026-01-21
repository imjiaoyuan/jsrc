import os
import argparse
import subprocess
import pandas as pd
from Bio import SeqIO
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Liberation Sans', 'DejaVu Sans', 'sans-serif']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-gff", nargs='+', required=True)
    parser.add_argument("-fa", nargs='+', required=True)
    parser.add_argument("-ids", required=True)
    parser.add_argument("-o", default="multi_species_synteny.png")
    args = parser.parse_args()

    num_sp = len(args.gff)
    sp_names = [os.path.splitext(os.path.basename(x))[0] for x in args.gff]
    bed_files = [f"{n}.bed" for n in sp_names]

    print("Converting GFF/GTF to BED...")
    for i in range(num_sp):
        gff_path = args.gff[i]
        out_bed = bed_files[i]
        
        if gff_path.lower().endswith(".gtf"):
            subprocess.run(["python", "-m", "jcvi.formats.gff", "bed", gff_path, "--type=transcript", "-o", out_bed])
        else:
            subprocess.run(["python", "-m", "jcvi.formats.gff", "bed", gff_path, "--type=mRNA", "-o", out_bed])
            
        if not os.path.exists(out_bed) or os.path.getsize(out_bed) < 10:
            print(f"Warning: {out_bed} is empty, trying type=gene or CDS...")
            if gff_path.lower().endswith(".gtf"):
                 subprocess.run(["python", "-m", "jcvi.formats.gff", "bed", gff_path, "--type=CDS", "--key=Parent", "-o", out_bed])
            else:
                 subprocess.run(["python", "-m", "jcvi.formats.gff", "bed", gff_path, "--type=gene", "-o", out_bed])

    bed_data = []
    seqids_lines = []
    
    print("Parsing BED and Fasta...")
    for i in range(num_sp):
        bed_df = pd.read_csv(bed_files[i], sep='\t', header=None, names=['chr', 'start', 'end', 'id', 'score', 'strand'], dtype=str)
        
        id_map = {}
        for x in bed_df['id']:
            s_x = str(x)
            id_map[s_x] = s_x
            if "transcript:" in s_x:
                clean = s_x.replace("transcript:", "")
                id_map[clean] = s_x
            if "." in s_x:
                no_ver = ".".join(s_x.split(".")[:-1])
                id_map[no_ver] = s_x
        
        bed_data.append(id_map)

        bed_chrs = set(bed_df['chr'].unique())
        fasta_chrs = []
        try:
            with open(args.fa[i], 'r') as f:
                for line in f:
                    if line.startswith('>'):
                        c = line.split()[0][1:]
                        if c in bed_chrs:
                            fasta_chrs.append(c)
        except Exception as e:
            print(f"Error reading fasta {args.fa[i]}: {e}")
        
        if not fasta_chrs:
            fasta_chrs = sorted(list(bed_chrs))
        
        seqids_lines.append(",".join(fasta_chrs[:20]))

    with open("seqids", "w") as f:
        f.write("\n".join(seqids_lines) + "\n")

    print("Generating simple links...")
    ids_df = pd.read_csv(args.ids, sep=',', header=None, dtype=str)

    for i in range(num_sp - 1):
        simple_file = f"{sp_names[i]}.{sp_names[i+1]}.simple"
        with open(simple_file, "w") as f:
            for _, row in ids_df.iterrows():
                if i+1 >= len(row): continue
                
                raw1 = str(row[i]).strip()
                raw2 = str(row[i+1]).strip()
                
                id1 = bed_data[i].get(raw1)
                id2 = bed_data[i+1].get(raw2)

                if id1 and id2:
                    f.write(f"{id1}\t{id2}\t#2b6cb0\n")

    with open("layout", "w") as f:
        f.write("# y, x, start, end, label, track_id, alignment\n")
        for i in range(num_sp):
            y = 0.9 - i * (0.8 / (num_sp - 1)) if num_sp > 1 else 0.5
            label = sp_names[i].split('_')[0].upper()[:4]
            f.write(f"{y:.2f}, 0.1, 0.8, 0, , {label}, top, {bed_files[i]}, center\n")
        f.write("# edges\n")
        for i in range(num_sp - 1):
            f.write(f"e, {i}, {i+1}, {sp_names[i]}.{sp_names[i+1]}.simple\n")

    print("Running JCVI plotting...")
    cmd = [
        "python", "-m", "jcvi.graphics.karyotype", "seqids", "layout",
        f"--outfile={args.o}", "--format=png", "--dpi=300"
    ]
    subprocess.run(cmd)

if __name__ == "__main__":
    main()