import random
from argparse import Namespace

import pytest

from jsrc.analyze.bootstrap_phylo import (
    _clade_key,
    _resample_columns,
    cmd,
)


class TestCladeKey:
    def test_sorted_leaves(self):
        from Bio.Phylo.BaseTree import Clade, Tree

        tree = Tree(root=Clade())
        tree.root.clades = [Clade(name="B"), Clade(name="A")]
        assert _clade_key(tree.root) == ("A", "B")

    def test_none_names_filtered(self):
        from Bio.Phylo.BaseTree import Clade, Tree

        tree = Tree(root=Clade())
        tree.root.clades = [Clade(name="X"), Clade(name=None)]
        assert _clade_key(tree.root) == ("X",)


class TestResampleColumns:
    def test_same_length(self, tmp_path):
        from Bio import SeqIO

        from jsrc.analyze.core import pad_alignment

        fa = tmp_path / "test.fa"
        fa.write_text(
            ">s1\nACGTACGT\n>s2\nACGTACGT\n>s3\nACGTACGT\n",
            encoding="utf-8",
        )
        records = list(SeqIO.parse(str(fa), "fasta"))
        aln = pad_alignment(records)
        rng = random.Random(42)
        resampled = _resample_columns(aln, rng)
        assert resampled.get_alignment_length() == aln.get_alignment_length()


class TestCmd:
    def test_basic_bootstrap(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGTACGTACGT\n>s2\nACGTACGTACG-\n>s3\nAC-TACGTACGT\n",
            encoding="utf-8",
        )
        args = Namespace(fa=str(fa), n=10, seed=42, o=None)
        cmd(args)
        out = capsys.readouterr().out
        assert "(" in out  # Newick format contains parentheses

    def test_output_to_file(self, tmp_path, capsys, caplog):
        import logging

        caplog.set_level(logging.INFO)
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGTACGTACGT\n>s2\nACGTACGTACG-\n>s3\nAC-TACGTACGT\n",
            encoding="utf-8",
        )
        out_file = tmp_path / "tree.nwk"
        args = Namespace(fa=str(fa), n=10, seed=42, o=str(out_file))
        cmd(args)
        assert out_file.exists()
        assert "(" in out_file.read_text()

    def test_needs_three_sequences(self, tmp_path):
        fa = tmp_path / "two.fa"
        fa.write_text(">s1\nACGT\n>s2\nACGT\n", encoding="utf-8")
        args = Namespace(fa=str(fa), n=10, seed=42, o=None)
        with pytest.raises(SystemExit):
            cmd(args)

    def test_n_must_be_positive(self, tmp_path):
        fa = tmp_path / "aln.fa"
        fa.write_text(">s1\nACGT\n>s2\nACGT\n>s3\nACGT\n", encoding="utf-8")
        args = Namespace(fa=str(fa), n=0, seed=42, o=None)
        with pytest.raises(SystemExit):
            cmd(args)
