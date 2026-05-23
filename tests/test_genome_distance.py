import json
from argparse import Namespace

import pytest

from jsrc.genome.distance import (
    _hamming_distance,
    _jukes_cantor_distance,
    _kimura_2p_distance,
    _p_distance,
    cmd,
)


class TestDistanceFunctions:
    def test_hamming_distance_identical(self):
        seq1 = "ATGC"
        seq2 = "ATGC"
        assert _hamming_distance(seq1, seq2) == 0

    def test_hamming_distance_different(self):
        seq1 = "ATGC"
        seq2 = "ATGG"
        assert _hamming_distance(seq1, seq2) == 1

    def test_hamming_distance_unequal_length_raises(self):
        seq1 = "ATGC"
        seq2 = "ATG"
        with pytest.raises(ValueError):
            _hamming_distance(seq1, seq2)

    def test_p_distance(self):
        seq1 = "ATGC"
        seq2 = "ATGG"
        assert _p_distance(seq1, seq2) == 0.25

    def test_p_distance_identical(self):
        seq1 = "ATGC"
        seq2 = "ATGC"
        assert _p_distance(seq1, seq2) == 0.0

    def test_jukes_cantor_distance(self):
        seq1 = "ATGC"
        seq2 = "ATGG"
        dist = _jukes_cantor_distance(seq1, seq2)
        assert dist > 0

    def test_jukes_cantor_distance_high_divergence(self):
        seq1 = "AAAA"
        seq2 = "TTTT"
        dist = _jukes_cantor_distance(seq1, seq2)
        assert dist == float("inf")

    def test_kimura_2p_distance(self):
        seq1 = "ATGC"
        seq2 = "GTGC"
        dist = _kimura_2p_distance(seq1, seq2)
        assert dist > 0

    def test_kimura_2p_distance_identical(self):
        seq1 = "ATGC"
        seq2 = "ATGC"
        assert _kimura_2p_distance(seq1, seq2) == 0.0


class TestDistanceCmd:
    def test_distance_hamming_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nATGG\n")

        args = Namespace(fa=str(fa), method="hamming", json=False)

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "seq1" in output
        assert "seq2" in output

    def test_distance_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nATGG\n")

        args = Namespace(fa=str(fa), method="p", json=True)

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
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["seq1"] == "seq1"
        assert data[0]["seq2"] == "seq2"
        assert "distance" in data[0]

    def test_distance_multiple_sequences(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nATGG\n>seq3\nATGA\n")

        args = Namespace(fa=str(fa), method="p", json=True)

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
        assert len(data) == 3

    def test_distance_insufficient_sequences_raises(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n")

        args = Namespace(fa=str(fa), method="p", json=False)

        with pytest.raises(ValueError):
            cmd(args)

    def test_distance_jc_method(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nATGG\n")

        args = Namespace(fa=str(fa), method="jc", json=True)

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
        assert len(data) == 1

    def test_distance_k2p_method(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nGTGC\n")

        args = Namespace(fa=str(fa), method="k2p", json=True)

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
        assert len(data) == 1
        assert data[0]["distance"] > 0
