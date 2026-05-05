import logging
from argparse import Namespace

from jsrc.seq.rename import cmd


def test_seq_rename_csv_mode(tmp_path, capsys, caplog):
    caplog.set_level(logging.INFO)
    fa = tmp_path / "in.fa"
    fa.write_text(">old1\nATGC\n>old2\nGGCC\n", encoding="utf-8")
    mapping = tmp_path / "map.csv"
    mapping.write_text("old1,new1\nold2,new2\n", encoding="utf-8")
    out = tmp_path / "out.fa"

    args = Namespace(
        fa=str(fa), mode="csv", map=str(mapping), gff=None, parent=None, o=str(out)
    )
    cmd(args)

    assert "Renamed 2 IDs" in caplog.text
    content = out.read_text()
    assert ">new1" in content
    assert ">new2" in content
    assert "ATGC" in content
    assert "GGCC" in content


def test_seq_rename_csv_partial(tmp_path, capsys):
    fa = tmp_path / "in.fa"
    fa.write_text(">old1\nATGC\n>unmatched\nGGCC\n", encoding="utf-8")
    mapping = tmp_path / "map.csv"
    mapping.write_text("old1,new1\n", encoding="utf-8")
    out = tmp_path / "out.fa"

    args = Namespace(
        fa=str(fa), mode="csv", map=str(mapping), gff=None, parent=None, o=str(out)
    )
    cmd(args)

    out_text = out.read_text()
    assert ">new1" in out_text
    assert ">unmatched" in out_text


def test_seq_rename_gff_mode(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    fa = tmp_path / "in.fa"
    fa.write_text(">tx1\nATGC\n>tx2\nGGCC\n", encoding="utf-8")
    gff = tmp_path / "anno.gff"
    gff.write_text(
        "##gff\nchr1\t.\tmRNA\t1\t10\t.\t+\t.\tID=tx1;Parent=gene1;\n"
        "chr1\t.\tmRNA\t20\t30\t.\t+\t.\tID=tx2;Parent=gene2;\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.fa"

    args = Namespace(
        fa=str(fa), mode="gff", map=None, gff=str(gff), parent="Parent", o=str(out)
    )
    cmd(args)

    assert "Renamed 2 IDs" in caplog.text
    content = out.read_text()
    assert ">gene1" in content
    assert ">gene2" in content
