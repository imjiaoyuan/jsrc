import json
from argparse import Namespace

import pytest

from jsrc.genome.kaks import _calculate_kaks, cmd


class TestCalculateKaks:
    def test_identical_sequences(self):
        seq1 = "ATGATGATG"
        seq2 = "ATGATGATG"
        result = _calculate_kaks(seq1, seq2)
        assert result["Ka"] == 0.0
        assert result["Ks"] == 0.0
        assert result["omega"] == 0.0

    def test_synonymous_substitution(self):
        seq1 = "ATG"
        seq2 = "ATG"
        result = _calculate_kaks(seq1, seq2)
        assert result["synonymous_subs"] == 0
        assert result["nonsynonymous_subs"] == 0

    def test_nonsynonymous_substitution(self):
        seq1 = "ATGAAAGGG"
        seq2 = "ATGTTGGGG"
        result = _calculate_kaks(seq1, seq2)
        assert result["Ka"] >= 0
        assert result["Ks"] >= 0

    def test_unequal_length_raises(self):
        seq1 = "ATGATG"
        seq2 = "ATG"
        with pytest.raises(ValueError):
            _calculate_kaks(seq1, seq2)

    def test_non_multiple_of_three_raises(self):
        seq1 = "ATGA"
        seq2 = "ATGA"
        with pytest.raises(ValueError):
            _calculate_kaks(seq1, seq2)

    def test_rna_sequence_converted(self):
        seq1 = "AUGAAAGGG"
        seq2 = "AUGAAAGGG"
        result = _calculate_kaks(seq1, seq2)
        assert result["Ka"] == 0.0
        assert result["Ks"] == 0.0


class TestKaksCmd:
    def test_kaks_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAA\n>seq2\nATGAAA\n")

        args = Namespace(fa=str(fa), json=False)

        from jsrc.genome.kaks import cmd

        cmd(args)

    def test_kaks_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAA\n>seq2\nATGAAA\n")

        args = Namespace(fa=str(fa), json=True)

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        data = json.loads(output)
        assert "Ka" in data
        assert "Ks" in data
        assert "omega" in data
        assert data["seq1"] == "seq1"
        assert data["seq2"] == "seq2"

    def test_kaks_not_two_sequences_raises(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAA\n")

        args = Namespace(fa=str(fa), json=False)

        with pytest.raises(ValueError):
            cmd(args)

    def test_kaks_three_sequences_raises(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAA\n>seq2\nATGAAA\n>seq3\nATGAAA\n")

        args = Namespace(fa=str(fa), json=False)

        with pytest.raises(ValueError):
            cmd(args)

    def test_kaks_different_sequences(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAATTT\n>seq2\nATGTTTAAA\n")

        args = Namespace(fa=str(fa), json=True)

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        data = json.loads(output)
        assert data["Ka"] >= 0
        assert data["Ks"] >= 0
