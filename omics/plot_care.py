import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True)
    parser.add_argument('-o', required=True)
    parser.add_argument('-n', type=int, default=15)
    parser.add_argument('-e', type=int, default=20)
    return parser.parse_args()

def parse_plantcare_file(filepath):
    data = {}
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) < 6:
                continue
            gene_id = parts[0].strip()
            element_name = parts[1].strip()
            if not element_name:
                continue
            try:
                position = int(parts[3])
                length = int(parts[4])
                if gene_id not in data:
                    data[gene_id] = []
                start = position
                end = position + length - 1
                data[gene_id].append({
                    'start': start,
                    'end': end,
                    'name': element_name,
                })
            except (IndexError, ValueError):
                continue
    return data

def plot_cis_elements(data, output_file, top_n, extend_bp):
    genes = sorted(data.keys())
    gene_count = len(genes)
    if gene_count == 0:
        return
    element_counts = {}
    for gene in genes:
        for elem in data[gene]:
            name = elem['name']
            element_counts[name] = element_counts.get(name, 0) + 1
    sorted_elements = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)
    top_elements = [elem[0] for elem in sorted_elements[:top_n]]
    colors = list(mcolors.TABLEAU_COLORS.values())
    if len(top_elements) > len(colors):
        cmap = plt.get_cmap('tab20')
        colors = [cmap(i) for i in np.linspace(0, 1, len(top_elements))]
    element_color_map = {elem: colors[i % len(colors)] for i, elem in enumerate(top_elements)}
    fig, ax = plt.subplots(figsize=(14, max(4, gene_count * 0.5)))
    y_positions = range(gene_count)
    for y, gene in zip(y_positions, genes):
        elements = data[gene]
        if not elements:
            continue
        all_starts = [e['start'] for e in elements if e['name'] in top_elements]
        all_ends = [e['end'] for e in elements if e['name'] in top_elements]
        if not all_starts:
            continue
        min_len = min(all_starts) - extend_bp
        max_len = max(all_ends) + extend_bp
        if min_len < max_len:
            ax.plot([min_len, max_len], [y, y], color='lightgray', linewidth=1, zorder=1)
        for e in elements:
            if e['name'] not in top_elements:
                continue
            start_pos = max(1, e['start'] - extend_bp)
            end_pos = e['end'] + extend_bp
            width = max(1, end_pos - start_pos)
            rect = mpatches.Rectangle(
                (start_pos, y - 0.25),
                width,
                0.5,
                facecolor=element_color_map[e['name']],
                linewidth=0,
                alpha=0.8,
                zorder=2
            )
            ax.add_patch(rect)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(genes, fontsize=10)
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel("Position in Promoter Region", fontsize=12)
    ax.set_ylim(-0.8, gene_count - 0.2)
    ax.invert_yaxis()
    
    if top_elements:
        legend_elements = []
        for elem in top_elements:
            count = element_counts.get(elem, 0)
            legend_elements.append(mpatches.Patch(color=element_color_map[elem], 
                                                  label=f"{elem} ({count})",
                                                  linewidth=0))
        ax.legend(handles=legend_elements, bbox_to_anchor=(1.02, 1), loc='upper left', 
                  fontsize=9, frameon=False)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

def main():
    args = get_args()
    data = parse_plantcare_file(args.i)
    plot_cis_elements(data, args.o, args.n, args.e)

if __name__ == "__main__":
    main()