from argparse import Namespace

import pytest

from jsrc.analyze.phylo import cmd


def test_phylo_requires_two_sequences(tmp_path):
    fasta = tmp_path / "one.fa"
    fasta.write_text(">s1\nATGC\n", encoding="utf-8")
    args = Namespace(fa=str(fasta), o=str(tmp_path / "x.nwk"), a="nj")
    with pytest.raises(SystemExit):
        cmd(args)
