import argparse
import sys
import seq, plot, analyze, pheno

def main():
    parser = argparse.ArgumentParser(
        prog='jsrc',
        description='Bioinformatics and phenotype analysis toolkit'
    )
    parser.add_argument('--version', action='version', version='1.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    seq_parser = subparsers.add_parser('seq', help='Sequence operations')
    seq_sub = seq_parser.add_subparsers(dest='seq_cmd')
    
    p = seq_sub.add_parser('extract', help='Extract sequences by ID list')
    p.add_argument('-fa', required=True, help='Input FASTA file')
    p.add_argument('-ids', required=True, help='ID list file (one per line)')
    p.add_argument('-o', required=True, help='Output FASTA file')
    p.set_defaults(func=seq.cmd_extract)
    
    p = seq_sub.add_parser('rename', help='Rename sequences using mapping file')
    p.add_argument('-fa', required=True, help='Input FASTA file')
    p.add_argument('-map', required=True, help='ID mapping file (CSV: old,new)')
    p.add_argument('-o', required=True, help='Output FASTA file')
    p.set_defaults(func=seq.cmd_rename)
    
    p = seq_sub.add_parser('rename-by-gff', help='Rename sequences based on GFF')
    p.add_argument('-fa', required=True, help='Input FASTA file')
    p.add_argument('-gff', required=True, help='GFF annotation file')
    p.add_argument('-parent', required=True, help='Parent attribute field name')
    p.add_argument('-o', required=True, help='Output FASTA file')
    p.set_defaults(func=seq.cmd_rename_by_gff)
    
    p = seq_sub.add_parser('translate', help='Extract CDS and translate to protein')
    p.add_argument('-fa', required=True, help='Genome FASTA file')
    p.add_argument('-gff', required=True, help='GFF annotation file')
    p.add_argument('-id', required=True, help='Gene ID field in GFF')
    p.add_argument('-o', required=True, help='Output protein FASTA')
    p.set_defaults(func=seq.cmd_translate)
    
    plot_parser = subparsers.add_parser('plot', help='Visualization')
    plot_sub = plot_parser.add_subparsers(dest='plot_cmd')
    
    p = plot_sub.add_parser('gene-structure', help='Plot gene structure diagram')
    p.add_argument('-gff', required=True, help='GFF annotation file')
    p.add_argument('-ids', required=True, help='Gene ID list file')
    p.add_argument('-o', required=True, help='Output PNG file')
    p.add_argument('-dpi', type=int, default=300, help='DPI (default: 300)')
    p.set_defaults(func=plot.cmd_gene_structure)
    
    p = plot_sub.add_parser('exon-structure', help='Plot exon structure')
    p.add_argument('-gff', required=True, help='GFF annotation file')
    p.add_argument('-ids', required=True, help='Gene ID list file')
    p.add_argument('-o', required=True, help='Output PNG file')
    p.add_argument('-dpi', type=int, default=300, help='DPI (default: 300)')
    p.set_defaults(func=plot.cmd_exon_structure)
    
    p = plot_sub.add_parser('chromosome-map', help='Plot chromosome map')
    p.add_argument('-gff', required=True, help='GFF annotation file')
    p.add_argument('-o', required=True, help='Output PNG file')
    p.add_argument('-dpi', type=int, default=300, help='DPI (default: 300)')
    p.set_defaults(func=plot.cmd_chromosome_map)
    
    p = plot_sub.add_parser('protein-domain', help='Plot protein domain architecture')
    p.add_argument('-tsv', required=True, help='Domain TSV file')
    p.add_argument('-o', required=True, help='Output PNG file')
    p.add_argument('-dpi', type=int, default=300, help='DPI (default: 300)')
    p.set_defaults(func=plot.cmd_protein_domain)
    
    p = plot_sub.add_parser('cis-element', help='Plot cis-regulatory elements')
    p.add_argument('-bed', required=True, help='BED file with elements')
    p.add_argument('-o', required=True, help='Output PNG file')
    p.add_argument('-dpi', type=int, default=300, help='DPI (default: 300)')
    p.set_defaults(func=plot.cmd_cis_element)
    
    analyze_parser = subparsers.add_parser('analyze', help='Analysis tools')
    analyze_sub = analyze_parser.add_subparsers(dest='analyze_cmd')
    
    p = analyze_sub.add_parser('phylo-tree', help='Build phylogenetic tree')
    p.add_argument('-fa', required=True, help='Input FASTA file')
    p.add_argument('-o', required=True, help='Output tree file')
    p.add_argument('-a', choices=['nj', 'ml'], default='nj', help='Algorithm (default: nj)')
    p.set_defaults(func=analyze.cmd_phylo_tree)
    
    p = analyze_sub.add_parser('motif', help='Find motifs using MEME')
    p.add_argument('-fa', required=True, help='Input FASTA file')
    p.add_argument('-o', required=True, help='Output directory')
    p.add_argument('-nmotifs', type=int, default=5, help='Number of motifs (default: 5)')
    p.add_argument('-minw', type=int, default=6, help='Min motif width (default: 6)')
    p.add_argument('-maxw', type=int, default=50, help='Max motif width (default: 50)')
    p.set_defaults(func=analyze.cmd_motif)
    
    pheno_parser = subparsers.add_parser('pheno', help='Phenotype image analysis')
    pheno_sub = pheno_parser.add_subparsers(dest='pheno_cmd')
    
    p = pheno_sub.add_parser('split-fruit', help='Segment fruit objects')
    p.add_argument('-i', required=True, help='Input image file')
    p.add_argument('-o', required=True, help='Output directory')
    p.add_argument('-size', type=int, default=800, help='Target size (default: 800)')
    p.set_defaults(func=pheno.cmd_split_fruit)
    
    p = pheno_sub.add_parser('split-fruit-raw', help='Segment fruit without resizing')
    p.add_argument('-i', required=True, help='Input image file')
    p.add_argument('-o', required=True, help='Output directory')
    p.set_defaults(func=pheno.cmd_split_fruit_raw)
    
    p = pheno_sub.add_parser('split-leaf', help='Segment leaf objects')
    p.add_argument('-i', required=True, help='Input image file')
    p.add_argument('-o', required=True, help='Output directory')
    p.add_argument('-size', type=int, default=800, help='Target size (default: 800)')
    p.set_defaults(func=pheno.cmd_split_leaf)
    
    p = pheno_sub.add_parser('split-leaf-edge', help='Extract leaf edges')
    p.add_argument('-i', required=True, help='Input image file')
    p.add_argument('-o', required=True, help='Output directory')
    p.set_defaults(func=pheno.cmd_split_leaf_edge)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        if args.command == 'seq' and not args.seq_cmd:
            seq_parser.print_help()
        elif args.command == 'plot' and not args.plot_cmd:
            plot_parser.print_help()
        elif args.command == 'analyze' and not args.analyze_cmd:
            analyze_parser.print_help()
        elif args.command == 'pheno' and not args.pheno_cmd:
            pheno_parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
