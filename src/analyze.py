import sys
import os
import tempfile
from Bio import SeqIO, AlignIO, Phylo
from common import sanitize_fasta_ids, check_external_tool

def cmd_phylo_tree(args):
    check_external_tool('mafft', 'conda install -c bioconda mafft')
    
    if args.a == 'ml':
        check_external_tool('FastTree', 'conda install -c bioconda fasttree')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        clean_fa = os.path.join(tmpdir, 'clean.fa')
        aln_fa = os.path.join(tmpdir, 'aligned.fa')
        
        id_map = sanitize_fasta_ids(args.fa, clean_fa)
        
        os.system(f'mafft --auto --quiet {clean_fa} > {aln_fa}')
        
        if args.a == 'nj':
            from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor
            
            alignment = AlignIO.read(aln_fa, 'fasta')
            calculator = DistanceCalculator('identity')
            dm = calculator.get_distance(alignment)
            constructor = DistanceTreeConstructor(calculator)
            tree = constructor.nj(dm)
            
        else:
            tree_file = os.path.join(tmpdir, 'tree.nwk')
            os.system(f'FastTree -nt -quiet {aln_fa} > {tree_file}')
            tree = Phylo.read(tree_file, 'newick')
        
        for clade in tree.find_clades():
            if clade.name and clade.name in id_map:
                clade.name = id_map[clade.name]
        
        Phylo.write(tree, args.o, 'newick')
    
    print(f"Phylogenetic tree ({args.a}) saved to {args.o}")

def cmd_motif(args):
    check_external_tool('meme', 'conda install -c bioconda meme')
    
    os.makedirs(args.o, exist_ok=True)
    
    cmd = f'meme {args.fa} -dna -oc {args.o} -nmotifs {args.nmotifs} -minw {args.minw} -maxw {args.maxw} -mod zoops'
    
    ret = os.system(cmd)
    
    if ret != 0:
        print(f"Error: MEME failed with exit code {ret}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Motif analysis complete. Results in {args.o}")
