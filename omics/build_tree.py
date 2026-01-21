import argparse
import sys
import subprocess
import os
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from Bio import AlignIO, Phylo, SeqIO
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-fa', required=True)
    parser.add_argument('-a', choices=['nj', 'ml'], default='nj')
    parser.add_argument('-on', required=True)
    parser.add_argument('-op', required=True)
    parser.add_argument('-t', type=int, default=4)
    return parser.parse_args()

def sanitize_fasta(input_fa, output_fa):
    records = []
    for record in SeqIO.parse(input_fa, "fasta"):
        clean_id = re.sub(r'[|:(),;\[\]\s]', '_', record.id)
        record.id = clean_id
        record.name = clean_id
        record.description = ""
        records.append(record)
    SeqIO.write(records, output_fa, "fasta")

def run_alignment(input_file, output_aln):
    subprocess.run(f"mafft --auto --quiet {input_file} > {output_aln}", shell=True, check=True)

def build_nj_tree(aln_file):
    alignment = AlignIO.read(aln_file, "fasta")
    calculator = DistanceCalculator('blosum62')
    constructor = DistanceTreeConstructor(calculator, 'nj')
    tree = constructor.build_tree(alignment)
    for clade in tree.find_clades():
        if clade.branch_length and clade.branch_length < 0:
            clade.branch_length = 0
    return tree

def build_ml_tree(aln_file, threads):
    out_nwk = aln_file + ".ml.nwk"
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = str(threads)
    cmd = f"FastTree -gamma -fastest -nosupport -out {out_nwk} {aln_file}"
    subprocess.run(cmd, shell=True, check=True, capture_output=True, env=env)
    tree = Phylo.read(out_nwk, "newick")
    if os.path.exists(out_nwk):
        os.remove(out_nwk)
    return tree

def visualize_tree(tree, out_pdf):
    num_terminals = len(tree.get_terminals())
    fig_height = max(10, num_terminals * 0.25)
    fig = plt.figure(figsize=(12, fig_height))
    ax = fig.add_subplot(1, 1, 1)
    Phylo.draw(tree, do_show=False, axes=ax, label_func=lambda x: x.name if x.is_terminal() else None)
    plt.title("Phylogenetic Tree")
    plt.tight_layout()
    plt.savefig(out_pdf)
    plt.close()

def main():
    args = get_args()
    clean_fa = args.fa + ".tmp.clean"
    aln_file = args.fa + ".tmp.aln"
    sanitize_fasta(args.fa, clean_fa)
    run_alignment(clean_fa, aln_file)
    if args.a == 'nj':
        tree = build_nj_tree(aln_file)
    else:
        tree = build_ml_tree(aln_file, args.t)
    Phylo.write(tree, args.on, "newick")
    visualize_tree(tree, args.op)
    for f in [clean_fa, aln_file]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()