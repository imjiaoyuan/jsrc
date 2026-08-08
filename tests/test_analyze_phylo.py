import random
from argparse import Namespace

import pytest

from jsrc.analyze.phylo import cmd
from jsrc.core import ValidationError


def _write_aln(tmp_path):
    fa = tmp_path / "aln.fa"
    fa.write_text(
        ">s1\nACGTACGTACGT\n>s2\nACGTACGTACG-\n>s3\nAC-TACGTACGT\n>s4\nACGTACGGACGT\n",
        encoding="utf-8",
    )
    return fa


def test_phylo_requires_two_sequences(tmp_path):
    fasta = tmp_path / "one.fa"
    fasta.write_text(">s1\nATGC\n", encoding="utf-8")
    args = Namespace(
        fa=str(fasta), o=str(tmp_path / "x.nwk"), a="nj", bootstrap=0, seed=42
    )
    with pytest.raises(ValidationError):
        cmd(args)


def test_phylo_bootstrap_adds_support_values(tmp_path):
    from Bio import Phylo

    out = tmp_path / "boot.nwk"
    args = Namespace(
        fa=str(_write_aln(tmp_path)), o=str(out), a="nj", bootstrap=20, seed=42
    )
    cmd(args)
    tree = Phylo.read(str(out), "newick")
    internals = [c for c in tree.get_nonterminals() if c is not tree.root]
    assert any(c.confidence is not None for c in internals)


def test_phylo_plain_tree_has_no_support(tmp_path):
    from Bio import Phylo

    out = tmp_path / "plain.nwk"
    args = Namespace(
        fa=str(_write_aln(tmp_path)), o=str(out), a="nj", bootstrap=0, seed=42
    )
    cmd(args)
    tree = Phylo.read(str(out), "newick")
    internals = [c for c in tree.get_nonterminals() if c is not tree.root]
    assert all(c.confidence is None for c in internals)


def test_phylo_bootstrap_needs_three_sequences(tmp_path):
    fa = tmp_path / "two.fa"
    fa.write_text(">s1\nACGT\n>s2\nACGT\n", encoding="utf-8")
    args = Namespace(fa=str(fa), o=None, a="nj", bootstrap=10, seed=42)
    with pytest.raises(ValidationError):
        cmd(args)


class TestCladeKey:
    def test_sorted_leaves(self):
        from Bio.Phylo.BaseTree import Clade, Tree

        from jsrc.analyze.phylo import _clade_key

        tree = Tree(root=Clade())
        tree.root.clades = [Clade(name="B"), Clade(name="A")]
        assert _clade_key(tree.root) == ("A", "B")

    def test_none_names_filtered(self):
        from Bio.Phylo.BaseTree import Clade, Tree

        from jsrc.analyze.phylo import _clade_key

        tree = Tree(root=Clade())
        tree.root.clades = [Clade(name="X"), Clade(name=None)]
        assert _clade_key(tree.root) == ("X",)


class TestResampleColumns:
    def test_same_length(self, tmp_path):
        from Bio import SeqIO

        from jsrc.analyze.core import pad_alignment
        from jsrc.analyze.phylo import _resample_columns

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
