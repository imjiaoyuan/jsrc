# jsrc Documentation

## 1. Quick Start

### 1.1 Installation

Use `uv` (recommended):

```bash
git clone https://github.com/imjiaoyuan/jsrc.git
cd jsrc
uv venv
uv sync --extra dev
uv run jsrc --help
```

Or with pip:

```bash
pip install -e .
jsrc --help
```

### 1.2 Deployment / Runtime Usage

Run commands directly:

```bash
jsrc <module> <subcommand> [options]
```

If using `uv` environment:

```bash
uv run jsrc <module> <subcommand> [options]
```

Optional module hot-plug controls:

```bash
JSRC_MODULES=seq,plot jsrc --help
JSRC_DISABLE_MODULES=grn jsrc --help
```

### 1.3 Development Workflow

```bash
git clone https://github.com/imjiaoyuan/jsrc.git
cd jsrc
uv venv
uv sync --extra dev
uv run jsrc --help
python -m compileall -q src
```

Project layout:

- `src/jsrc/seq` bioinformatics sequence tools
- `src/jsrc/analyze` statistics and analysis tools
- `src/jsrc/plot` plotting and visualization
- `src/jsrc/gs` genomic selection dataset/build/train workflow
- `src/jsrc/grn` GRN conversion/service utilities
- `src/jsrc/vision` image and shape analysis
- `src/jsrc/text` general text processing

## 2. Module Docs

- [Sequence Module](./module-seq.md)
- [Analyze Module](./module-analyze.md)
- [Plot Module](./module-plot.md)
- [GS Module](./module-gs.md)
- [GRN Module](./module-grn.md)
- [Vision Module](./module-vision.md)
- [Text Module](./module-text.md)

## 3. Global CLI Behavior

- Main form: `jsrc <module> <command> ...`
- Some commands print to terminal by default; some require `-o` outputs.
- For text commands, `-i` is optional; if omitted, data is read from `stdin`.
