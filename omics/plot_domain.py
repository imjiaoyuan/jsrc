import argparse
import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True, help='Input NCBI CD-search result file')
    parser.add_argument('-o', required=True, help='Output image file (e.g., domains.png)')
    return parser.parse_args()

def parse_ncbi_file(filepath):
    data = {}
    unique_domains = set()
    
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.strip().split('\t')
            if parts[0] == 'Query':
                continue
                
            try:
                query_raw = parts[0]
                if '>' in query_raw:
                    gene_id = query_raw.split('>')[1].strip()
                else:
                    gene_id = query_raw
                
                start = int(parts[3])
                end = int(parts[4])
                domain_name = parts[8]
                
                if gene_id not in data:
                    data[gene_id] = []
                
                data[gene_id].append({
                    'start': start,
                    'end': end,
                    'name': domain_name
                })
                unique_domains.add(domain_name)
                
            except (IndexError, ValueError):
                continue
                
    return data, sorted(list(unique_domains))

def plot_domains(data, unique_domains, output_file):
    genes = sorted(data.keys())
    gene_count = len(genes)
    
    if gene_count == 0:
        return

    fig, ax = plt.subplots(figsize=(12, max(4, gene_count * 0.4)))
    
    colors = list(mcolors.TABLEAU_COLORS.values())
    if len(unique_domains) > len(colors):
        import numpy as np
        cmap = plt.get_cmap('tab20')
        colors = [cmap(i) for i in np.linspace(0, 1, len(unique_domains))]
    
    domain_color_map = {dom: colors[i % len(colors)] for i, dom in enumerate(unique_domains)}
    
    y_positions = range(gene_count)
    
    for y, gene in zip(y_positions, genes):
        domains = data[gene]
        
        max_len = max([d['end'] for d in domains]) if domains else 0
        ax.plot([1, max_len], [y, y], color='gray', linewidth=1, zorder=1)
        
        for d in domains:
            width = d['end'] - d['start']
            rect = mpatches.Rectangle(
                (d['start'], y - 0.25), 
                width, 
                0.5, 
                color=domain_color_map[d['name']], 
                alpha=0.9, 
                zorder=2
            )
            ax.add_patch(rect)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(genes)
    ax.set_xlabel("Amino Acid Position")
    ax.set_ylim(-0.5, gene_count - 0.5)
    ax.invert_yaxis()
    
    legend_patches = [mpatches.Patch(color=domain_color_map[d], label=d) for d in unique_domains]
    ax.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)

def main():
    args = get_args()
    data, domains = parse_ncbi_file(args.i)
    plot_domains(data, domains, args.o)

if __name__ == "__main__":
    main()