import argparse
import subprocess
import sys
import os
import shutil
import re
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from Bio import SeqIO

def run_meme(input_file, output_dir, n_motifs, minw, maxw):
    if not shutil.which("meme"):
        sys.exit("Error: 'meme' not found. Install via: conda install -c bioconda meme")
    
    cmd = [
        "meme", input_file,
        "-protein",
        "-oc", output_dir,
        "-nmotifs", str(n_motifs),
        "-minw", str(minw),
        "-maxw", str(maxw),
        "-mod", "zoops"
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def parse_meme_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    motifs = {}
    for motif in root.findall(".//motif"):
        m_id = motif.get("id")
        m_alt = motif.get("alt")
        width = int(motif.get("width"))
        color = motif.get("color") 
        motifs[m_id] = {'alt': m_alt, 'width': width, 'color': None}

    sequences = {}
    for seq in root.findall(".//scanned_sites_summary/scanned_site"):
        seq_id = seq.get("sequence_id")
        seq_len = 0 
        
        sites = []
        for site in seq.findall("scanned_site_motif"):
            m_id = site.get("motif_id")
            pos = int(site.get("position"))
            sites.append({'motif_id': m_id, 'start': pos})
        
        sequences[seq_id] = {'len': 0, 'sites': sites}

    return motifs, sequences

def get_real_seq_lengths(fasta_file, sequences):
    for record in SeqIO.parse(fasta_file, "fasta"):
        clean_id = record.id.split()[0]
        if clean_id in sequences:
            sequences[clean_id]['len'] = len(record.seq)
        elif record.id in sequences:
             sequences[record.id]['len'] = len(record.seq)
    return sequences

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def plot_motifs(motifs, sequences, output_file):
    sorted_ids = sorted(sequences.keys(), key=natural_sort_key)
    num_seqs = len(sorted_ids)
    
    if num_seqs == 0:
        return

    fig_height = max(4, num_seqs * 0.5)
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    colors = [
        '#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', 
        '#FFFF33', '#A65628', '#F781BF', '#999999', '#66C2A5'
    ]
    
    motif_keys = sorted(motifs.keys(), key=lambda x: int(x.replace('motif_', '')))
    for i, m_key in enumerate(motif_keys):
        motifs[m_key]['color'] = colors[i % len(colors)]

    max_len = 0
    for seq_id in sorted_ids:
        length = sequences[seq_id]['len']
        if length > max_len:
            max_len = length

    for i, seq_id in enumerate(sorted_ids):
        data = sequences[seq_id]
        length = data['len']
        y_pos = num_seqs - 1 - i
        
        ax.plot([0, length], [y_pos, y_pos], color='black', linewidth=1, zorder=1)
        ax.text(-max_len * 0.01, y_pos, seq_id, ha='right', va='center', fontsize=10)
        
        for site in data['sites']:
            m_id = site['motif_id']
            start = site['start']
            width = motifs[m_id]['width']
            color = motifs[m_id]['color']
            
            rect = patches.Rectangle(
                (start, y_pos - 0.2), width, 0.4,
                linewidth=0, facecolor=color, zorder=2
            )
            ax.add_patch(rect)

    ax.set_xlim(-max_len * 0.05, max_len * 1.15)
    ax.set_ylim(-0.5, num_seqs)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks([])
    ax.set_xlabel('Amino Acid Position')

    legend_patches = []
    for m_key in motif_keys:
        m_info = motifs[m_key]
        legend_patches.append(patches.Patch(color=m_info['color'], label=m_info['alt']))
    
    ax.legend(handles=legend_patches, loc='upper left', bbox_to_anchor=(1.0, 1.0))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    parser.add_argument('-o', required=True)
    parser.add_argument('-n', default=10, type=int)
    parser.add_argument('-minw', default=6, type=int)
    parser.add_argument('-maxw', default=50, type=int)
    args = parser.parse_args()

    meme_out_dir = args.o + "_meme_data"
    
    run_meme(args.i, meme_out_dir, args.n, args.minw, args.maxw)
    
    xml_file = os.path.join(meme_out_dir, "meme.xml")
    if not os.path.exists(xml_file):
        sys.exit("Error: meme.xml not generated.")

    motifs, sequences = parse_meme_xml(xml_file)
    sequences = get_real_seq_lengths(args.i, sequences)
    
    plot_file = args.o + ".png" if not args.o.endswith('.png') else args.o
    plot_motifs(motifs, sequences, plot_file)

if __name__ == "__main__":
    main()