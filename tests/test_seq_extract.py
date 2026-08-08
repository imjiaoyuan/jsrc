import logging
from argparse import Namespace

import pytest
from Bio import SeqIO

from jsrc.core import ResourceNotFoundError
from jsrc.seq.extract import cmd


def _make_args(tmp_path, *, omit=None):
    """Build extract args; omit one input file to test missing-file handling."""
    fa = tmp_path / "genome.fa"
    gff = tmp_path / "anno.gff"
    ids = tmp_path / "ids.txt"
    if omit != "fa":
        fa.write_text(">chr1\nATGCGGTTAA\n", encoding="utf-8")
    if omit != "gff":
        gff.write_text(
            "chr1\tsrc\tCDS\t1\t3\t.\t+\t.\tParent=gene1\n", encoding="utf-8"
        )
    if omit != "ids":
        ids.write_text("gene1\n", encoding="utf-8")
    return Namespace(
        fa=str(fa),
        gff=str(gff),
        ids=str(ids),
        o=str(tmp_path / "out.fa"),
        feature="CDS",
        match="Parent",
    )


def test_extract_missing_fasta_raises_resource_not_found(tmp_path):
    args = _make_args(tmp_path, omit="fa")
    with pytest.raises(ResourceNotFoundError):
        cmd(args)


def test_extract_missing_gff_raises_resource_not_found(tmp_path):
    args = _make_args(tmp_path, omit="gff")
    with pytest.raises(ResourceNotFoundError):
        cmd(args)


def test_extract_missing_ids_raises_resource_not_found(tmp_path):
    args = _make_args(tmp_path, omit="ids")
    with pytest.raises(ResourceNotFoundError):
        cmd(args)


def test_seq_extract_basic_flow(tmp_path, capsys, caplog):
    caplog.set_level(logging.INFO)
    fa = tmp_path / "genome.fa"
    gff = tmp_path / "anno.gff"
    ids = tmp_path / "ids.txt"
    out = tmp_path / "out.fa"

    fa.write_text(">chr1\nATGCGGTTAA\n", encoding="utf-8")
    gff.write_text(
        "chr1\tsrc\tCDS\t1\t3\t.\t+\t.\tParent=gene1\n"
        "chr1\tsrc\tCDS\t4\t6\t.\t+\t.\tParent=gene1\n",
        encoding="utf-8",
    )
    ids.write_text("gene1\n", encoding="utf-8")

    args = Namespace(
        fa=str(fa),
        gff=str(gff),
        ids=str(ids),
        o=str(out),
        feature="CDS",
        match="Parent",
    )
    cmd(args)

    assert "Extracted 1/1 sequences" in caplog.text
    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert recs[0].id == "gene1"
    assert str(recs[0].seq) == "ATGCGG"
