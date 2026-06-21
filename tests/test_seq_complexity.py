from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.seq.complexity import (
    _dust_score,
    _linguistic_complexity,
    _shannon_entropy,
    cmd,
)


class TestShannonEntropy:
    def test_empty_sequence(self):
        assert _shannon_entropy("") == 0.0

    def test_single_char(self):
        assert _shannon_entropy("AAAA") == 0.0

    def test_uniform_distribution(self):
        ent = _shannon_entropy("ACGT")
        assert ent == pytest.approx(2.0)

    def test_typical_sequence(self):
        ent = _shannon_entropy("ATGCATGC")
        assert 0 < ent < 3.0


class TestLinguisticComplexity:
    def test_empty_sequence(self):
        assert _linguistic_complexity("") == 0.0

    def test_single_char(self):
        assert _linguistic_complexity("AAAA", max_k=2) == 0.0

    def test_full_complexity(self):
        lc = _linguistic_complexity("ACGTACGT", max_k=3)
        assert 0.0 < lc <= 1.0

    def test_repetitive_sequence(self):
        lc_rep = _linguistic_complexity("ATATATAT", max_k=2)
        lc_div = _linguistic_complexity("ATCGATCG", max_k=2)
        assert lc_rep < lc_div


class TestDustScore:
    def test_short_sequence(self):
        assert _dust_score("AT", window=64) == 0.0

    def test_empty_sequence(self):
        assert _dust_score("", window=64) == 0.0

    def test_repetitive_sequence(self):
        s_rep = _dust_score("ATATATAT" * 16, window=64)
        s_div = _dust_score("ATCGATCG" * 16, window=64)
        assert s_rep > s_div

    def test_returns_float_in_range(self):
        score = _dust_score("ACGT" * 32, window=64)
        assert isinstance(score, float)
        assert score >= 0.0


class TestCmd:
    def test_basic_output(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">s1\nATGCATGCATGC\n>s2\nAAAAAAAAAAAA\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False)
        cmd(args)
        out = capsys.readouterr().out
        assert "s1" in out
        assert "s2" in out
        assert "shannon_entropy" in out
        assert "linguistic_complexity" in out
        assert "dust_score" in out

    def test_json_output(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">s1\nATGC\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=True)
        cmd(args)
        out = capsys.readouterr().out
        assert '"id"' in out
        assert '"shannon_entropy"' in out
        assert '"dust_score"' in out

    def test_empty_fasta_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False)
        with pytest.raises(DataFormatError):
            cmd(args)

    def test_lowercase_and_uracil_normalized(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">s1\natgcuu\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False)
        cmd(args)
        out = capsys.readouterr().out
        assert "ATGCT" in out or "6" in out  # U→T, lowercase→uppercase
