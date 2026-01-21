import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse
import sys

def parse_attributes(attr_string):
    attrs = {}
    for item in attr_string.strip().strip(';').split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            attrs[key] = value
    return attrs

def get_gene_data(gff_file, target_ids):
    target_set = set(target_ids)
    valid_mrna = {}
    coords = {tid: [] for tid in target_ids}
    
    try:
        with open(gff_file, 'r') as f:
            for line in f:
                if line.startswith('#'): continue
                parts = line.strip().split('\t')
                if len(parts) < 9: continue

                ftype, attr = parts[2], parse_attributes(parts[8])
                
                if ftype == 'mRNA':
                    pid = attr.get('Parent')
                    mid = attr.get('ID')
                    if pid in target_set:
                        valid_mrna[mid] = pid
                
                elif ftype in ['CDS', 'exon', 'five_prime_UTR', 'three_prime_UTR']:
                    pid = attr.get('Parent')
                    if pid in valid_mrna:
                        gid = valid_mrna[pid]
                        coords[gid].append((int(parts[3]), int(parts[4])))
    except Exception:
        sys.exit(1)
    return coords

def plot_genes(data, ids, output):
    valid_ids = [i for i in ids if data[i]]
    if not valid_ids: return

    fig, ax = plt.subplots(figsize=(12, max(4, len(ids) * 0.7)))
    max_bp = 0
    h = 0.4

    for i, gid in enumerate(ids):
        region = sorted(data[gid])
        y = len(ids) - 1 - i
        if not region: continue
        
        g_start, g_end = region[0][0], region[-1][1]
        max_bp = max(max_bp, g_end - g_start)

        for j in range(len(region) - 1):
            curr_end, next_start = region[j][1], region[j+1][0]
            if next_start > curr_end:
                ax.add_patch(patches.Rectangle(
                    (curr_end - g_start, y - h/2), next_start - curr_end, h,
                    facecolor='#ffb74d', edgecolor='none', zorder=1
                ))

        for start, end in region:
            ax.add_patch(patches.Rectangle(
                (start - g_start, y - h/2), end - start, h,
                facecolor='#fE6F61', edgecolor='none', zorder=2
            ))

    ax.legend(handles=[
        patches.Patch(facecolor='#fE6F61', label='CDS'),
        patches.Patch(facecolor='#ffb74d', label='Intron')
    ], loc='upper right', frameon=False)

    ax.set_yticks(range(len(ids)))
    ax.set_yticklabels(ids[::-1])
    ax.set_xlabel('Relative Position (bp)')
    ax.set_ylim(-1, len(ids))
    ax.set_xlim(-200, max_bp + 200)
    
    for s in ['top', 'right', 'left']: ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)

    plt.tight_layout()
    plt.savefig(output, dpi=300)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('-g', required=True)
    p.add_argument('-i', required=True)
    p.add_argument('-o', required=True)
    args = p.parse_args()

    with open(args.i) as f:
        ids = [l.strip() for l in f if l.strip()]
    ids = list(dict.fromkeys(ids))

    data = get_gene_data(args.g, ids)
    plot_genes(data, ids, args.o)