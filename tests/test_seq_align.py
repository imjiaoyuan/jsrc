from argparse import Namespace

import pytest

from jsrc.core import ValidationError
from jsrc.seq.align import cmd


class TestCmd:
    def test_global_identical(self, tmp_path, capsys):
        fa1 = tmp_path / "s1.fa"
        fa1.write_text(">s1\nACGTACGT\n", encoding="utf-8")
        fa2 = tmp_path / "s2.fa"
        fa2.write_text(">s1\nACGTACGT\n", encoding="utf-8")

        args = Namespace(
            fa=None,
            fa1=str(fa1),
            fa2=str(fa2),
            mode="global",
            match=None,
            mismatch=None,
            gap_open=None,
            gap_extend=None,
            top=1,
            score_only=False,
        )
        cmd(args)
        out = capsys.readouterr().out
        assert "ACGTACGT" in out

    def test_score_only(self, tmp_path, capsys):
        fa1 = tmp_path / "s1.fa"
        fa1.write_text(">s1\nACGT\n", encoding="utf-8")
        fa2 = tmp_path / "s2.fa"
        fa2.write_text(">s1\nACGT\n", encoding="utf-8")

        args = Namespace(
            fa=None,
            fa1=str(fa1),
            fa2=str(fa2),
            mode="global",
            match=None,
            mismatch=None,
            gap_open=None,
            gap_extend=None,
            top=1,
            score_only=True,
        )
        cmd(args)
        out = capsys.readouterr().out.strip()
        assert float(out) == 4.0

    def test_local_mode(self, tmp_path, capsys):
        fa1 = tmp_path / "s1.fa"
        fa1.write_text(">s1\nAAAAAAAAACGTAAAA\n", encoding="utf-8")
        fa2 = tmp_path / "s2.fa"
        fa2.write_text(">s1\nACGT\n", encoding="utf-8")

        args = Namespace(
            fa=None,
            fa1=str(fa1),
            fa2=str(fa2),
            mode="local",
            match=None,
            mismatch=None,
            gap_open=None,
            gap_extend=None,
            top=1,
            score_only=True,
        )
        cmd(args)
        out = capsys.readouterr().out.strip()
        assert float(out) >= 4.0

    def test_single_fa_two_sequences(self, tmp_path, capsys):
        fa = tmp_path / "both.fa"
        fa.write_text(">s1\nACGT\n>s2\nACGT\n", encoding="utf-8")
        args = Namespace(
            fa=str(fa),
            fa1=None,
            fa2=None,
            mode="global",
            match=None,
            mismatch=None,
            gap_open=None,
            gap_extend=None,
            top=1,
            score_only=True,
        )
        cmd(args)
        out = capsys.readouterr().out.strip()
        assert float(out) == 4.0

    def test_missing_input_raises(self):
        args = Namespace(
            fa=None,
            fa1=None,
            fa2=None,
            mode="global",
            match=None,
            mismatch=None,
            gap_open=None,
            gap_extend=None,
            top=1,
            score_only=False,
        )
        with pytest.raises(ValidationError):
            cmd(args)

    def test_gap_penalties(self, tmp_path, capsys):
        fa1 = tmp_path / "s1.fa"
        fa1.write_text(">s1\nACGT\n", encoding="utf-8")
        fa2 = tmp_path / "s2.fa"
        fa2.write_text(">s1\nACG\n", encoding="utf-8")

        args = Namespace(
            fa=None,
            fa1=str(fa1),
            fa2=str(fa2),
            mode="global",
            match=None,
            mismatch=None,
            gap_open=-2.0,
            gap_extend=-0.5,
            top=1,
            score_only=True,
        )
        cmd(args)
        out = capsys.readouterr().out.strip()
        assert float(out) < 4.0  # gap penalty reduces score
