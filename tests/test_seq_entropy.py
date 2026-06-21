import json
from argparse import Namespace

import pytest

from jsrc.seq.entropy import _col_entropy, _conservation, cmd


class TestColEntropy:
    def test_empty_column(self):
        assert _col_entropy([]) == 0.0

    def test_single_char(self):
        assert _col_entropy(["A", "A", "A"]) == 0.0

    def test_uniform_column(self):
        ent = _col_entropy(["A", "C", "G", "T"])
        assert ent == 2.0

    def test_mixed_column(self):
        ent = _col_entropy(["A", "A", "C", "C"])
        assert ent == 1.0


class TestConservation:
    def test_empty_column(self):
        assert _conservation([]) == 0.0

    def test_fully_conserved(self):
        assert _conservation(["A", "A", "A"]) == 1.0

    def test_half_conserved(self):
        assert _conservation(["A", "A", "C", "C"]) == 0.5


class TestCmd:
    def test_basic_output(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGT\n>s2\nACGT\n>s3\nACGT\n", encoding="utf-8"
        )
        args = Namespace(fa=str(fa), json=False, summary=False)
        cmd(args)
        out = capsys.readouterr().out
        assert "sequence_count" in out
        assert "alignment_length" in out
        assert "mean_entropy" in out
        assert "mean_conservation" in out
        assert "position" in out

    def test_summary_flag(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGT\n>s2\nACGT\n>s3\nACGT\n", encoding="utf-8"
        )
        args = Namespace(fa=str(fa), json=False, summary=True)
        cmd(args)
        out = capsys.readouterr().out
        assert "sequence_count" in out
        assert "position" not in out

    def test_json_output(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGT\n>s2\nACGT\n>s3\nACGT\n", encoding="utf-8"
        )
        args = Namespace(fa=str(fa), json=True, summary=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["sequence_count"] == 3
        assert data["alignment_length"] == 4
        assert "columns" in data

    def test_unequal_lengths_padded(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGT\n>s2\nACG\n>s3\nAC\n", encoding="utf-8"
        )
        args = Namespace(fa=str(fa), json=True, summary=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["alignment_length"] == 4

    def test_needs_two_sequences(self, tmp_path):
        fa = tmp_path / "single.fa"
        fa.write_text(">s1\nACGT\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False, summary=True)
        with pytest.raises(SystemExit):
            cmd(args)

    def test_entropy_nonzero_for_mixed_column(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(
            ">s1\nACGT\n>s2\nTTTT\n>s3\nAAAA\n", encoding="utf-8"
        )
        args = Namespace(fa=str(fa), json=True, summary=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["mean_entropy"] > 0.0
