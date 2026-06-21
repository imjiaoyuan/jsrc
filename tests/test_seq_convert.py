from argparse import Namespace

import pytest

from jsrc.core import ValidationError
from jsrc.seq.convert import cmd


def test_convert_genbank_to_fasta(tmp_path, capsys, caplog):
    import logging

    caplog.set_level(logging.INFO)

    gb = tmp_path / "test.gb"
    gb.write_text(
        "LOCUS       test       12 bp    DNA\n"
        "FEATURES             Location/Qualifiers\n"
        "ORIGIN\n"
        "        1 acgtacgtac gt\n"
        "//\n",
        encoding="utf-8",
    )
    out_fa = tmp_path / "out.fa"
    args = Namespace(input=str(gb), from_fmt="genbank", to_fmt="fasta", o=str(out_fa))
    cmd(args)

    assert out_fa.exists()
    content = out_fa.read_text(encoding="utf-8")
    assert content.startswith(">")


def test_missing_input_raises(tmp_path):
    args = Namespace(
        input="/nonexistent/file.gb",
        from_fmt="genbank",
        to_fmt="fasta",
        o="/tmp/out.fa",
    )
    with pytest.raises(ValidationError):
        cmd(args)
