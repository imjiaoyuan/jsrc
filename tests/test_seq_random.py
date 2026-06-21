from argparse import Namespace

import pytest

from jsrc.core import ValidationError
from jsrc.seq.random import cmd


def test_default_dna_generation(tmp_path, capsys):
    args = Namespace(type="dna", n=3, l=100, gc=0.5, seed=42, o=None)
    cmd(args)
    out = capsys.readouterr().out
    assert out.count(">") == 3
    # Sequences should only contain ACGT
    lines = [line for line in out.split("\n") if line and not line.startswith(">")]
    for line in lines:
        assert set(line.upper()) <= {"A", "C", "G", "T"}


def test_protein_generation(tmp_path, capsys):
    args = Namespace(type="protein", n=2, l=50, gc=0.5, seed=42, o=None)
    cmd(args)
    out = capsys.readouterr().out
    assert out.count(">") == 2


def test_output_to_file(tmp_path, capsys):
    out_file = tmp_path / "random.fa"
    args = Namespace(type="dna", n=5, l=20, gc=0.5, seed=42, o=str(out_file))
    cmd(args)
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert content.count(">") == 5


def test_reproducible_seed(tmp_path, capsys):
    args1 = Namespace(type="dna", n=1, l=50, gc=0.5, seed=123, o=None)
    cmd(args1)
    out1 = capsys.readouterr().out

    args2 = Namespace(type="dna", n=1, l=50, gc=0.5, seed=123, o=None)
    cmd(args2)
    out2 = capsys.readouterr().out

    assert out1 == out2


def test_different_seed_different_output(tmp_path, capsys):
    args1 = Namespace(type="dna", n=1, l=50, gc=0.5, seed=1, o=None)
    cmd(args1)
    out1 = capsys.readouterr().out

    args2 = Namespace(type="dna", n=1, l=50, gc=0.5, seed=2, o=None)
    cmd(args2)
    out2 = capsys.readouterr().out

    assert out1 != out2


def test_gc_zero_yields_only_at(tmp_path, capsys):
    args = Namespace(type="dna", n=1, l=200, gc=0.0, seed=42, o=None)
    cmd(args)
    out = capsys.readouterr().out
    lines = [line for line in out.split("\n") if line and not line.startswith(">")]
    seq = lines[0].upper()
    assert set(seq) <= {"A", "T"}


def test_gc_one_yields_only_gc(tmp_path, capsys):
    args = Namespace(type="dna", n=1, l=200, gc=1.0, seed=42, o=None)
    cmd(args)
    out = capsys.readouterr().out
    lines = [line for line in out.split("\n") if line and not line.startswith(">")]
    seq = lines[0].upper()
    assert set(seq) <= {"G", "C"}


def test_invalid_gc_raises(tmp_path):
    args = Namespace(type="dna", n=1, l=10, gc=1.5, seed=42, o=None)
    with pytest.raises(ValidationError):
        cmd(args)


def test_invalid_n_raises(tmp_path):
    args = Namespace(type="dna", n=0, l=10, gc=0.5, seed=42, o=None)
    with pytest.raises(ValidationError):
        cmd(args)
