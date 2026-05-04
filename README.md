# jsrc

Bioinformatics analysis toolkit with modular subcommands.

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

## Module Layout

```text
src/jsrc/
  seq/     # sequence module (core.py + command modules)
  plot/    # plotting module (core.py + command modules)
  analyze/ # analysis module (core.py + command modules)
  grn/     # GRN module (core.py + command modules)
```

Each module is independently loadable by CLI, with optional hot-plug controls:

```bash
# Enable only specific modules
JSRC_MODULES=seq,plot jsrc --help

# Disable selected modules
JSRC_DISABLE_MODULES=grn jsrc --help
```

## Commands

### seq

```bash
# Extract feature sequences by IDs from genome+GFF (default: feature=CDS, match=Parent)
jsrc seq extract -fa genome.fa -gff genes.gff -ids ids.txt -feature CDS -match Parent -o cds.fa

# Extract full gene sequences by gene IDs
jsrc seq extract -fa genome.fa -gff genes.gff -ids genes.txt -feature gene -match ID -o genes.fa

# Rename FASTA IDs using CSV mapping old_id,new_id
jsrc seq rename -fa input.fa -mode csv -map mapping.csv -o output.fa

# Rename FASTA IDs using GFF mRNA->parent mapping
jsrc seq rename -fa transcripts.fa -mode gff -gff genes.gff -parent Parent -o output.fa

# Extract CDS from GFF and translate to proteins
jsrc seq translate -fa genome.fa -gff genes.gff -id ID -o proteins.fa

# Extract promoter sequences with configurable upstream/downstream bp
jsrc seq promoter -fa genome.fa -gff genes.gff -ids genes.txt -id ID -feature gene -up 2000 -down 200 -o promoters.fa
```

### plot

```bash
# Plot CDS-based gene structure
jsrc plot gene -gff genes.gff -ids genes.txt -o gene_structure.png

# Plot exon-based structure
jsrc plot exon -gff genes.gff -ids genes.txt -o exon_structure.png

# Plot chromosome map with gene positions
jsrc plot chromosome -gff genes.gff -o chromosome_map.png

# Plot chromosome map only for genes in ID list
jsrc plot chromosome -gff genes.gff -ids genes.txt -o chromosome_map_selected.png

# Plot protein domain architecture from TSV
jsrc plot domain -tsv domains.tsv -o protein_domains.png

# Plot cis-regulatory elements from BED
jsrc plot cis -bed elements.bed -o cis_elements.png
```

### analyze

```bash
# Build phylogenetic tree (default NJ)
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a nj

# Build phylogenetic tree with UPGMA
jsrc analyze phylo -fa sequences.fa -o tree.nwk -a upgma

# Motif analysis with built-in pure-python k-mer method
jsrc analyze motif -fa promoters.fa -o motif_output -nmotifs 5
```

### grn

```bash
# Convert GRN edge table to JSON links
jsrc grn to_json -i grn.tsv -o viewer/json/grn.json -t network

# Convert annotation table to JSON dictionary
jsrc grn to_json -i annotation.tsv -o viewer/json/annotation.json -t annotation

# Initialize empty local GRN viewer scaffold
jsrc grn init -o viewer

# Serve local GRN viewer through HTTP
jsrc grn serve -d viewer -p 8000
```
