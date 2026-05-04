# Copilot Instructions for jsrc

A modular CLI toolkit for bioinformatics and data analysis.

## Important Rules

- **Never commit code** — Copilot must not directly create commits, push, or publish. The user handles all git operations, version bumps, and PyPI releases.
- **Only suggest changes** — Present code changes as suggestions; let the user decide when and how to commit them.

## Project Structure

## Project Structure

```
omics/     - Bioinformatics tools (sequences, phylogeny, visualization)
pheno/     - Phenotype analysis (image segmentation for fruits/leaves)
misc/      - Miscellaneous utilities
```

## Dependencies

The project requires Python 3.10+ with the following core dependencies:
- **biopython** - Sequence manipulation and analysis
- **matplotlib** - All visualization scripts
- **opencv-python** - Image processing (pheno module)
- **numpy** - Numerical operations
- **pandas** - Data handling

Install via: `uv sync` (uses uv.lock and pyproject.toml)

## Key Conventions

### Script Organization
- **All scripts are standalone CLI tools** - Each `.py` file is an independent executable with its own argument parser
- **No shared modules** - Scripts are self-contained; there's no internal library structure
- **Standard pattern**: `argparse` for CLI → processing function → output to file

### Matplotlib Configuration
- **Always use Agg backend** at the top of visualization scripts:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  import matplotlib.pyplot as plt
  ```
- This ensures scripts work in headless environments (servers, containers)

### BioPython Usage
- Parse sequences with `SeqIO.parse(file, "fasta")`
- Extract sequence IDs with `.id.split()[0]` to get first word (ignores descriptions)
- Use case-insensitive ID matching with `.lower().split('.')[0]` for version-agnostic lookups

### GFF/GTF Parsing
- Parse attributes manually with string splitting (no dedicated library)
- Standard pattern: `parts[8]` contains attributes as `key=value;` pairs
- Extract features by type: `parts[2]` (common: 'mRNA', 'CDS', 'exon', 'gene')
- Parent-child relationships: Use `Parent=` attribute to link features

### Argument Naming Patterns
- `-fa` - FASTA file input
- `-gff` - GFF/GTF annotation file
- `-i` or `-ids` - ID list file (one per line)
- `-o` - Output file (image or data)
- `-on` - Newick tree output (phylogeny scripts)
- `-op` - PDF/PNG plot output
- `-a` - Algorithm choice (e.g., 'nj' or 'ml' for tree building)
- `-t` - Thread count

### Image Processing (pheno module)
- Input: RGB images of fruits or leaves
- Process: HSV color space conversion → thresholding → morphological operations → contour detection
- Output: RGBA PNGs with transparent backgrounds (alpha channel from mask)
- Save contours as `.npy` files with `--save_npy` flag for reproducibility
- Filter contours by: area (relative to image size), solidity, extent, aspect ratio

### External Dependencies
Some scripts require external bioinformatics tools:
- `build_tree.py` - MAFFT (alignment) and optionally FastTree (ML trees)
- `calc_motif.py` - MEME suite
- `plot_synteny.py` - JCVI toolkit (`python -m jcvi.formats.gff`)

Scripts check for these with `shutil.which()` or subprocess calls and exit with helpful error messages if missing.

## Module-Specific Notes

### omics/
Bioinformatics utilities focused on sequence analysis and genomic visualization:

**Sequence manipulation:**
- `fa_extract.py` - Extract sequences by ID (handles version suffixes, finds longest if duplicates)
- `fa_rename.py` - Rename FASTA headers
- `fa_rename_gff.py` - Rename using GFF mapping
- `fa_trans.py` - Extract CDS from GFF and translate to protein

**Phylogenetics:**
- `build_tree.py` - Construct phylogenetic trees (NJ or ML)
  - Sanitizes FASTA IDs (removes special chars: `|:(),;[]`)
  - Uses MAFFT for alignment
  - NJ via BioPython, ML via FastTree
  - Auto-generates visualization PDF

**Motif analysis:**
- `calc_motif.py` - Find protein motifs using MEME, visualize results

**Genomic visualization:**
- `plot_gene.py` - Gene structure diagrams (exons/introns from GFF)
  - Parses mRNA → CDS hierarchy
  - Relative positioning (all genes aligned to start)
  - Color scheme: `#fE6F61` (CDS), `#ffb74d` (introns)
- `plot_struct.py` - Similar to plot_gene with alternate styling
- `plot_chrom.py` - Chromosome maps with gene positions (uses PIL, not matplotlib)
- `plot_domain.py` - Protein domain architecture (NCBI CD-search format)
- `plot_synteny.py` - Multi-species synteny plots (requires JCVI)

**Common visualization pattern:**
```python
fig, ax = plt.subplots(figsize=(12, height))
# ... plotting ...
plt.tight_layout()
plt.savefig(output, dpi=300)
plt.close()
```

### pheno/
Image segmentation tools for plant phenotyping:

**Fruit segmentation:**
- `split_fruit.py` - Extract individual fruits from images
  - HSV color space: brightness (V>30) and saturation (S>40) filters
  - Multi-stage morphological operations (open → close → open)
  - Filtering: removes artificial objects (blue/purple hues), extreme aspect ratios
  - Auto-naming: parses filename (e.g., "base_1_2_3" → "base", "base-1", "base-2")
  - Sorts extracted objects left-to-right by bounding box
- `split_fruit_raw.py` - Similar but preserves original image dimensions

**Leaf segmentation:**
- `split_leaf.py` - Segment leaves using LAB color space
  - Uses A-channel (green-red) with Otsu thresholding
  - Filters by solidity, extent, aspect ratio
- `split_leaf_edge.py` - Extract leaf edges

**Common pattern:**
```python
# HSV/LAB conversion → threshold → morphology → contours → filter → extract ROI → RGBA output
mask = cv2.inRange(hsv, lower, upper)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# Filter by area, solidity, extent...
rgba = cv2.merge([b, g, r, alpha])
cv2.imwrite(output, rgba)
```

### misc/
- `clean_bloat.py` - System cleanup utility
- `plot_heart.py` - Parametric heart curve visualization
- `plot_rose.R` - R script for rose plots

## Adding New Scripts

When creating new utilities:

1. **Follow the standalone pattern** - Self-contained script with argparse
2. **Use Agg backend** - If using matplotlib for visualization
3. **Handle missing external tools** - Check with `shutil.which()` and provide installation hints
4. **Match naming conventions** - Use standard argument flags (`-fa`, `-gff`, `-o`, etc.)
5. **Clean up temp files** - Remove intermediate files (alignment files, sanitized inputs, etc.)
6. **Set matplotlib backend early** - Before any pyplot imports
7. **Use relative coordinates** - For gene/domain plots (subtract minimum position)
8. **Validate inputs** - Check file existence, handle empty results gracefully
