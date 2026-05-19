import logging
from argparse import Namespace

from Bio import SeqIO
from jsrc.seq.translate import cmd


def test_seq_translate_basic(tmp_path, capsys, caplog):
    caplog.set_level(logging.INFO)
    fa = tmp_path / "genome.fa"
    fa.write_text(">chr1\nATGGCCACTTAA\n", encoding="utf-8")
    gff = tmp_path / "anno.gff"
    gff.write_text(
        "chr1\tsrc\tCDS\t1\t3\t.\t+\t.\tID=cds1;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t4\t6\t.\t+\t.\tID=cds2;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t7\t9\t.\t+\t.\tID=cds3;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t10\t12\t.\t+\t.\tID=cds4;Parent=gene1;\n",
        encoding="utf-8",
    )
    out = tmp_path / "proteins.fa"

    args = Namespace(fa=str(fa), gff=str(gff), id="Parent", o=str(out))
    cmd(args)

    assert "Translated 1 genes" in caplog.text
    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert recs[0].id == "gene1"
    assert "MAT" in str(recs[0].seq)


def test_seq_translate_reverse_strand(tmp_path, capsys):

    fa = tmp_path / "genome.fa"
    fa.write_text(">chr1\nTTAAGTGGCAT\n", encoding="utf-8")
    gff = tmp_path / "anno.gff"
    gff.write_text(
        "chr1\tsrc\tCDS\t1\t3\t.\t-\t.\tID=cds1;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t4\t6\t.\t-\t.\tID=cds2;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t7\t9\t.\t-\t.\tID=cds3;Parent=gene1;\n"
        "chr1\tsrc\tCDS\t10\t12\t.\t-\t.\tID=cds4;Parent=gene1;\n",
        encoding="utf-8",
    )
    out = tmp_path / "proteins.fa"

    args = Namespace(fa=str(fa), gff=str(gff), id="Parent", o=str(out))
    cmd(args)

    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert "MPL" in str(recs[0].seq)
