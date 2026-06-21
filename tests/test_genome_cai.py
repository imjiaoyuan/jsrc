import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.genome.cai import cmd


def test_basic_cai(tmp_path, capsys):
    # Reference: highly expressed genes (biased codon usage)
    ref = tmp_path / "ref.fa"
    ref.write_text(">ref1\n" + "GCCGCCGCCGCC" * 4 + "\n", encoding="utf-8")

    # Query: same codon usage → CAI ≈ 1.0
    query = tmp_path / "query.fa"
    query.write_text(">gene1\n" + "GCCGCCGCCGCC" * 4 + "\n", encoding="utf-8")

    args = Namespace(fa=str(query), reference=str(ref), json=True)
    cmd(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["id"] == "gene1"
    assert data[0]["cai"] == pytest.approx(1.0, abs=0.01)


def test_different_codon_usage_lower_cai(tmp_path, capsys):
    # Reference: uses both GCC and GCA for alanine, but biased toward GCC
    ref = tmp_path / "ref.fa"
    ref.write_text(">ref1\n" + "GCC" * 16 + "GCA" * 4 + "\n", encoding="utf-8")

    # Query: only uses the less-preferred codon → lower CAI
    query = tmp_path / "query.fa"
    query.write_text(">gene1\n" + "GCA" * 20 + "\n", encoding="utf-8")

    args = Namespace(fa=str(query), reference=str(ref), json=True)
    cmd(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["cai"] < 1.0


def test_multiple_genes(tmp_path, capsys):
    ref = tmp_path / "ref.fa"
    ref.write_text(">ref1\n" + "GCC" * 15 + "GCA" * 5 + "\n", encoding="utf-8")

    query = tmp_path / "query.fa"
    query.write_text(
        ">gene1\n" + "GCC" * 10 + "\n"
        ">gene2\n" + "GCA" * 10 + "\n",
        encoding="utf-8",
    )

    args = Namespace(fa=str(query), reference=str(ref), json=True)
    cmd(args)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
    # GCC is preferred in reference → gene1 (GCC) should have higher CAI
    assert data[0]["cai"] > data[1]["cai"]


def test_table_output(tmp_path, capsys):
    ref = tmp_path / "ref.fa"
    ref.write_text(">ref1\n" + "GCC" * 20 + "\n", encoding="utf-8")
    query = tmp_path / "query.fa"
    query.write_text(">gene1\n" + "GCC" * 10 + "\n", encoding="utf-8")

    args = Namespace(fa=str(query), reference=str(ref), json=False)
    cmd(args)
    out = capsys.readouterr().out
    assert "id" in out
    assert "codon_count" in out
    assert "cai" in out
    assert "gene1" in out


def test_empty_reference_raises(tmp_path):
    ref = tmp_path / "empty.fa"
    ref.write_text("", encoding="utf-8")
    query = tmp_path / "query.fa"
    query.write_text(">gene1\n" + "GCC" * 10 + "\n", encoding="utf-8")

    args = Namespace(fa=str(query), reference=str(ref), json=True)
    with pytest.raises(DataFormatError):
        cmd(args)


def test_empty_query_raises(tmp_path):
    ref = tmp_path / "ref.fa"
    ref.write_text(">ref1\n" + "GCC" * 20 + "\n", encoding="utf-8")
    query = tmp_path / "empty.fa"
    query.write_text("", encoding="utf-8")

    args = Namespace(fa=str(query), reference=str(ref), json=True)
    with pytest.raises(DataFormatError):
        cmd(args)
