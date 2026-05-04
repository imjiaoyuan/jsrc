import sys
import pandas as pd
from common import setup_matplotlib, get_gene_structure, parse_gff_attributes, natural_sort_key
plt = setup_matplotlib()

def cmd_gene_structure(args):
    with open(args.ids, 'r') as f:
        gene_ids = [line.strip() for line in f if line.strip()]
    
    coords = get_gene_structure(args.gff, gene_ids, feature_types=['CDS'])
    
    gene_ids_sorted = sorted(gene_ids, key=natural_sort_key)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(gene_ids_sorted) * 0.5)))
    
    for i, gid in enumerate(gene_ids_sorted):
        y = len(gene_ids_sorted) - i - 1
        if gid not in coords or not coords[gid]:
            continue
        
        cds_list = sorted(coords[gid])
        gstart = min(c[0] for c in cds_list)
        gend = max(c[1] for c in cds_list)
        
        ax.plot([gstart, gend], [y, y], 'k-', linewidth=1)
        
        for start, end in cds_list:
            ax.add_patch(plt.Rectangle((start, y-0.15), end-start, 0.3, facecolor='steelblue', edgecolor='black'))
    
    ax.set_yticks(range(len(gene_ids_sorted)))
    ax.set_yticklabels(gene_ids_sorted[::-1])
    ax.set_xlabel('Genomic Position')
    ax.set_title('Gene Structure')
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    print(f"Gene structure plot saved to {args.o}")

def cmd_exon_structure(args):
    with open(args.ids, 'r') as f:
        gene_ids = [line.strip() for line in f if line.strip()]
    
    coords = get_gene_structure(args.gff, gene_ids, feature_types=['exon'])
    
    gene_ids_sorted = sorted(gene_ids, key=natural_sort_key)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(gene_ids_sorted) * 0.5)))
    
    for i, gid in enumerate(gene_ids_sorted):
        y = len(gene_ids_sorted) - i - 1
        if gid not in coords or not coords[gid]:
            continue
        
        exon_list = sorted(coords[gid])
        gstart = min(c[0] for c in exon_list)
        gend = max(c[1] for c in exon_list)
        
        ax.plot([gstart, gend], [y, y], 'k-', linewidth=1)
        
        for start, end in exon_list:
            ax.add_patch(plt.Rectangle((start, y-0.2), end-start, 0.4, facecolor='green', edgecolor='black'))
    
    ax.set_yticks(range(len(gene_ids_sorted)))
    ax.set_yticklabels(gene_ids_sorted[::-1])
    ax.set_xlabel('Genomic Position')
    ax.set_title('Exon Structure')
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    print(f"Exon structure plot saved to {args.o}")

def cmd_chromosome_map(args):
    chr_lengths = {}
    gene_positions = []
    
    with open(args.gff, 'r') as f:
        for line in f:
            if line.startswith('##sequence-region'):
                parts = line.strip().split()
                if len(parts) >= 4:
                    chr_name = parts[1]
                    chr_len = int(parts[3])
                    chr_lengths[chr_name] = chr_len
            elif not line.startswith('#'):
                parts = line.strip().split('\t')
                if len(parts) >= 9 and parts[2] == 'gene':
                    chrom = parts[0]
                    start = int(parts[3])
                    end = int(parts[4])
                    
                    attr = parse_gff_attributes(parts[8])
                    gene_id = attr.get('ID', '')
                    
                    gene_positions.append({
                        'chr': chrom,
                        'start': start,
                        'end': end,
                        'id': gene_id
                    })
                    
                    if chrom not in chr_lengths:
                        chr_lengths[chrom] = max(chr_lengths.get(chrom, 0), end)
    
    chr_sorted = sorted(chr_lengths.keys(), key=natural_sort_key)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(chr_sorted) * 0.5)))
    
    for i, chrom in enumerate(chr_sorted):
        y = len(chr_sorted) - i - 1
        chr_len = chr_lengths[chrom]
        
        ax.add_patch(plt.Rectangle((0, y-0.2), chr_len, 0.4, facecolor='lightgray', edgecolor='black'))
        
        chr_genes = [g for g in gene_positions if g['chr'] == chrom]
        for gene in chr_genes:
            mid = (gene['start'] + gene['end']) / 2
            ax.plot([mid, mid], [y-0.15, y+0.15], 'r-', linewidth=0.5, alpha=0.5)
    
    ax.set_yticks(range(len(chr_sorted)))
    ax.set_yticklabels(chr_sorted[::-1])
    ax.set_xlabel('Position (bp)')
    ax.set_title('Chromosome Map')
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    print(f"Chromosome map saved to {args.o}")

def cmd_protein_domain(args):
    df = pd.read_csv(args.tsv, sep='\t', comment='#')
    
    required_cols = ['protein', 'domain', 'start', 'end']
    if not all(col in df.columns for col in required_cols):
        print(f"Error: TSV must have columns: {', '.join(required_cols)}", file=sys.stderr)
        sys.exit(1)
    
    proteins = sorted(df['protein'].unique(), key=natural_sort_key)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(proteins) * 0.5)))
    
    for i, prot in enumerate(proteins):
        y = len(proteins) - i - 1
        prot_domains = df[df['protein'] == prot]
        
        max_pos = prot_domains['end'].max()
        ax.plot([0, max_pos], [y, y], 'k-', linewidth=2)
        
        for _, row in prot_domains.iterrows():
            start = row['start']
            end = row['end']
            domain = row['domain']
            
            ax.add_patch(plt.Rectangle((start, y-0.2), end-start, 0.4, 
                                      facecolor='orange', edgecolor='black', alpha=0.7))
            ax.text((start+end)/2, y, domain, ha='center', va='center', fontsize=8)
    
    ax.set_yticks(range(len(proteins)))
    ax.set_yticklabels(proteins[::-1])
    ax.set_xlabel('Position (aa)')
    ax.set_title('Protein Domain Architecture')
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    print(f"Protein domain plot saved to {args.o}")

def cmd_cis_element(args):
    elements = []
    
    with open(args.bed, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                elements.append({
                    'chr': parts[0],
                    'start': int(parts[1]),
                    'end': int(parts[2]),
                    'name': parts[3]
                })
    
    chromosomes = sorted(set(e['chr'] for e in elements), key=natural_sort_key)
    
    fig, ax = plt.subplots(figsize=(12, max(6, len(chromosomes) * 0.5)))
    
    for i, chrom in enumerate(chromosomes):
        y = len(chromosomes) - i - 1
        chr_elements = [e for e in elements if e['chr'] == chrom]
        
        if chr_elements:
            max_pos = max(e['end'] for e in chr_elements)
            ax.plot([0, max_pos], [y, y], 'k-', linewidth=1)
            
            for elem in chr_elements:
                mid = (elem['start'] + elem['end']) / 2
                ax.plot([mid, mid], [y-0.3, y+0.3], 'b-', linewidth=2)
                ax.text(mid, y+0.35, elem['name'], ha='center', fontsize=7, rotation=45)
    
    ax.set_yticks(range(len(chromosomes)))
    ax.set_yticklabels(chromosomes[::-1])
    ax.set_xlabel('Position (bp)')
    ax.set_title('Cis-regulatory Elements')
    
    plt.tight_layout()
    plt.savefig(args.o, dpi=args.dpi, bbox_inches='tight')
    plt.close()
    print(f"Cis-element plot saved to {args.o}")
