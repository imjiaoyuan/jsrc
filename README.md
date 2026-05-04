# jsrc

Bioinformatics and phenotype analysis toolkit

## Installation

```bash
pip install jsrc
```

Or install from source:

```bash
git clone https://github.com/imjiaoyuan/jsrc.git
cd jsrc
pip install -e .
```

## Commands

**Sequence Operations**

```bash
jsrc seq extract -fa genome.fa -ids ids.txt -o output.fa
jsrc seq rename -fa input.fa -map mapping.csv -o output.fa
jsrc seq rename-by-gff -fa transcripts.fa -gff genes.gff -parent Parent -o output.fa
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa
```

**Visualization**

```bash
jsrc plot gene-structure -gff genes.gff -ids genes.txt -o gene_structure.png
jsrc plot exon-structure -gff genes.gff -ids genes.txt -o exon_structure.png
jsrc plot chromosome-map -gff genes.gff -o chromosome_map.png
jsrc plot protein-domain -tsv domains.tsv -o protein_domains.png
jsrc plot cis-element -bed elements.bed -o cis_elements.png
```

**Analysis Tools**

```bash
jsrc analyze phylo-tree -fa sequences.fa -o tree.nwk -a nj
jsrc analyze phylo-tree -fa sequences.fa -o tree.nwk -a ml
jsrc analyze motif -fa promoters.fa -o motif_output -nmotifs 5
```

**Phenotype Image Analysis**

```bash
jsrc pheno split-fruit -i fruit_image.jpg -o output_dir
jsrc pheno split-fruit-raw -i fruit_image.jpg -o output_dir
jsrc pheno split-leaf -i leaf_image.jpg -o output_dir
jsrc pheno split-leaf-edge -i leaf_image.jpg -o output_dir
```