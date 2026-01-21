import argparse
import re
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ids', required=True)
    parser.add_argument('-gff', required=True)
    parser.add_argument('-fmt', default='transcript_id')
    parser.add_argument('-o', default='gene_structure_solid.png')
    args = parser.parse_args()

    target_ids = set()
    with open(args.ids, 'r') as f:
        for line in f:
            if line.strip():
                target_ids.add(line.strip())

    gene_data = {}

    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t')
            if len(parts) < 9:
                continue

            feature = parts[2]
            if feature != 'exon':
                continue

            try:
                start = int(parts[3])
                end = int(parts[4])
                strand = parts[6]
            except ValueError:
                continue

            attributes = parts[8]
            pattern = args.fmt + r'\s+"?([^";]+)"?'
            match = re.search(pattern, attributes)
            
            if not match and '=' in attributes:
                pattern_gff = args.fmt + r'=([^;]+)'
                match = re.search(pattern_gff, attributes)

            if match:
                tid = match.group(1)
                if tid in target_ids:
                    if tid not in gene_data:
                        gene_data[tid] = {'strand': strand, 'exons': []}
                    gene_data[tid]['exons'].append((start, end))

    if not gene_data:
        return

    sorted_ids = sorted(gene_data.keys(), key=natural_sort_key)
    
    num_genes = len(sorted_ids)
    fig_height = max(4, num_genes * 0.6)
    
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    max_gene_len = 0
    
    exon_color = '#FFA07A'
    intron_color = "#D3D3D3"
    
    block_height = 0.4

    for i, tid in enumerate(sorted_ids):
        info = gene_data[tid]
        exons = sorted(info['exons'], key=lambda x: x[0])
        strand = info['strand']
        
        if not exons:
            continue
            
        g_min = min(e[0] for e in exons)
        g_max = max(e[1] for e in exons)
        g_len = g_max - g_min
        
        if g_len > max_gene_len:
            max_gene_len = g_len
            
        y_pos = num_genes - 1 - i
        
        introns = []
        for j in range(len(exons) - 1):
            intron_start = exons[j][1] + 1
            intron_end = exons[j+1][0] - 1
            if intron_end >= intron_start:
                introns.append((intron_start, intron_end))

        for start, end in introns:
            width = end - start + 1
            if strand == '+':
                x_start = start - g_min
            else:
                x_start = g_max - end
            
            rect = patches.Rectangle(
                (x_start, y_pos - block_height/2), width, block_height,
                linewidth=0, facecolor=intron_color, zorder=1
            )
            ax.add_patch(rect)

        for start, end in exons:
            width = end - start + 1
            if strand == '+':
                x_start = start - g_min
            else:
                x_start = g_max - end
                
            rect = patches.Rectangle(
                (x_start, y_pos - block_height/2), width, block_height,
                linewidth=0, facecolor=exon_color, zorder=2
            )
            ax.add_patch(rect)
            
        ax.text(-max_gene_len * 0.02, y_pos, tid, ha='right', va='center', fontsize=10)

    ax.set_xlim(-max_gene_len * 0.05, max_gene_len * 1.05)
    ax.set_ylim(-0.5, num_genes - 0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_yticks([])
    ax.set_xlabel('Gene Length (bp) [5\' -> 3\']')
    
    legend_elements = [
        patches.Patch(facecolor=exon_color, label='Exon'),
        patches.Patch(facecolor=intron_color, label='Intron')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.0, 1.0), frameon=False)
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=300)

if __name__ == "__main__":
    main()