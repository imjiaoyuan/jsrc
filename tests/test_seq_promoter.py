import logging
from argparse import Namespace

from Bio import SeqIO
from jsrc.seq.promoter import cmd


def test_seq_promoter_forward_strand(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    fa = tmp_path / "genome.fa"
    fa.write_text(">chr1\nNNNNNNNNNNATGGCCTAA\n", encoding="utf-8")
    gff = tmp_path / "anno.gff"
    gff.write_text("chr1\tsrc\tgene\t11\t19\t.\t+\t.\tID=gene1;\n", encoding="utf-8")
    ids = tmp_path / "ids.txt"
    ids.write_text("gene1\n", encoding="utf-8")
    out = tmp_path / "promoters.fa"

    args = Namespace(
        fa=str(fa),
        gff=str(gff),
        ids=str(ids),
        o=str(out),
        id="ID",
        feature="gene",
        up=5,
        down=0,
    )
    cmd(args)

    assert "Extracted 1 promoter sequences" in caplog.text
    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert recs[0].id == "gene1"
    assert str(recs[0].seq) == "NNNNN"


def test_seq_promoter_reverse_strand(tmp_path):

    fa = tmp_path / "genome.fa"
    fa.write_text(">chr1\nAAAACCTTTTGGGGGCCCCC\n", encoding="utf-8")
    gff = tmp_path / "anno.gff"
    gff.write_text("chr1\tsrc\tgene\t1\t5\t.\t-\t.\tID=gene1;\n", encoding="utf-8")
    ids = tmp_path / "ids.txt"
    ids.write_text("gene1\n", encoding="utf-8")
    out = tmp_path / "promoters.fa"

    args = Namespace(
        fa=str(fa),
        gff=str(gff),
        ids=str(ids),
        o=str(out),
        id="ID",
        feature="gene",
        up=5,
        down=0,
    )
    cmd(args)

    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert recs[0].id == "gene1"

    assert str(recs[0].seq) == "AAAAG"
