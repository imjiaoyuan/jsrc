import json
from argparse import Namespace

import pytest

from jsrc.core import ValidationError
from jsrc.seq.qc import cmd


def test_seq_qc_fasta_basic(tmp_path, capsys):
    fa = tmp_path / "test.fa"
    fa.write_text(">s1\nATGCGC\n>s2\nGGCC\n", encoding="utf-8")

    args = Namespace(fa=fa, fq=None, gs=None, json=False)
    cmd(args)

    out = capsys.readouterr().out
    assert "[fasta]" in out
    assert "sequence_count\t2" in out
    assert "total_bases\t10" in out
    assert "gc_percent" in out


def test_seq_qc_fasta_json(tmp_path, capsys):
    fa = tmp_path / "test.fa"
    fa.write_text(">s1\nATGC\n>s2\nGGCC\n", encoding="utf-8")

    args = Namespace(fa=fa, fq=None, gs=None, json=True)
    cmd(args)

    payload = json.loads(capsys.readouterr().out)
    assert "fasta" in payload
    assert payload["fasta"]["sequence_count"] == 2
    assert payload["fasta"]["total_bases"] == 8


def test_seq_qc_no_input_raises(tmp_path):
    args = Namespace(fa=None, fq=None, gs=None, json=False)
    with pytest.raises(ValidationError):
        cmd(args)


def test_seq_qc_fastq_basic(tmp_path, capsys):
    fq = tmp_path / "test.fq"
    fq.write_text("@r1\nATGC\n+\nIIII\n@r2\nGGCC\n+\nIIII\n", encoding="utf-8")

    args = Namespace(fa=None, fq=[str(fq)], gs=None, json=False)
    cmd(args)

    out = capsys.readouterr().out
    assert "[fastq]" in out
    assert "reads\t2" in out
    assert "bases\t8" in out


def test_seq_qc_fastq_with_depth(tmp_path, capsys):
    fq = tmp_path / "test.fq"
    fq.write_text("@r1\nATGC\n+\nIIII\n", encoding="utf-8")

    args = Namespace(fa=None, fq=[str(fq)], gs=100, json=True)
    cmd(args)

    payload = json.loads(capsys.readouterr().out)
    assert payload["fastq"]["reads"] == 1
    assert payload["fastq"]["estimated_depth"] == 4.0 / 100
