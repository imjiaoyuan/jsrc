from argparse import Namespace

from Bio import SeqIO

from jsrc.seq.extract import cmd


def test_seq_extract_basic_flow(tmp_path, capsys):
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

    captured = capsys.readouterr().out
    assert "Extracted 1/1 sequences" in captured
    recs = list(SeqIO.parse(str(out), "fasta"))
    assert len(recs) == 1
    assert recs[0].id == "gene1"
    assert str(recs[0].seq) == "ATGCGG"
