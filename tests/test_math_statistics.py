from argparse import Namespace

import pytest

from jsrc.math.statistics import cmd


def test_statistics_empty_data_fails(tmp_path):
    tsv = tmp_path / "empty.tsv"
    tsv.write_text("x\n", encoding="utf-8")
    args = Namespace(input=str(tsv), sep=None, col="1", output=None)
    with pytest.raises(SystemExit):
        cmd(args)
