import json
from argparse import Namespace

import pytest

from jsrc.genome.stats import _calculate_n50_l50, _count_gaps, cmd


class TestCalculateN50L50:
    def test_basic_n50_l50(self):
        lengths = [100, 200, 300, 400, 500]
        n50, l50 = _calculate_n50_l50(lengths)
        assert n50 == 400
        assert l50 == 2

    def test_single_sequence(self):
        lengths = [1000]
        n50, l50 = _calculate_n50_l50(lengths)
        assert n50 == 1000
        assert l50 == 1

    def test_empty_list(self):
        lengths = []
        n50, l50 = _calculate_n50_l50(lengths)
        assert n50 == 0
        assert l50 == 0

    def test_equal_lengths(self):
        lengths = [100, 100, 100, 100]
        n50, l50 = _calculate_n50_l50(lengths)
        assert n50 == 100
        assert l50 == 2


class TestCountGaps:
    def test_no_gaps(self):
        seq = "ATCGATCG"
        result = _count_gaps(seq)
        assert result["n_count"] == 0
        assert result["gap_count"] == 0
        assert result["min_gap"] == 0
        assert result["max_gap"] == 0
        assert result["mean_gap"] == 0.0

    def test_single_gap(self):
        seq = "ATCGNNNGATCG"
        result = _count_gaps(seq)
        assert result["n_count"] == 3
        assert result["gap_count"] == 1
        assert result["min_gap"] == 3
        assert result["max_gap"] == 3
        assert result["mean_gap"] == 3.0

    def test_multiple_gaps(self):
        seq = "ATCGNNGATCGNNNNG"
        result = _count_gaps(seq)
        assert result["n_count"] == 6
        assert result["gap_count"] == 2
        assert result["min_gap"] == 2
        assert result["max_gap"] == 4
        assert result["mean_gap"] == 3.0

    def test_gap_at_start(self):
        seq = "NNATCG"
        result = _count_gaps(seq)
        assert result["n_count"] == 2
        assert result["gap_count"] == 1
        assert result["min_gap"] == 2

    def test_gap_at_end(self):
        seq = "ATCGNN"
        result = _count_gaps(seq)
        assert result["n_count"] == 2
        assert result["gap_count"] == 1
        assert result["max_gap"] == 2

    def test_lowercase_n(self):
        seq = "ATCGnnnGATCG"
        result = _count_gaps(seq)
        assert result["n_count"] == 3
        assert result["gap_count"] == 1


class TestStatsCmd:
    def test_stats_basic(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATCGATCG\n>seq2\nATCGATCGATCG\n")

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

        assert data["num_sequences"] == 2
        assert data["total_length"] == 20
        assert data["min_length"] == 8
        assert data["max_length"] == 12
        assert data["mean_length"] == 10.0
        assert data["gc_percent"] == 50.0

    def test_stats_with_gaps(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATCGNNNATCG\n")

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

        assert data["n_count"] == 3
        assert data["gap_count"] == 1
        assert data["min_gap_length"] == 3
        assert data["max_gap_length"] == 3

    def test_stats_n50_calculation(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(
            ">seq1\n"
            + "A" * 10
            + "\n"
            + ">seq2\n"
            + "A" * 20
            + "\n"
            + ">seq3\n"
            + "A" * 30
            + "\n"
            + ">seq4\n"
            + "A" * 40
            + "\n"
            + ">seq5\n"
            + "A" * 50
            + "\n"
        )

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

        assert data["n50"] == 40
        assert data["l50"] == 2

    def test_stats_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")

        args = Namespace(fa=str(fa), json=False)

        with pytest.raises(SystemExit):
            cmd(args)

    def test_stats_text_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATCGATCG\n")

        args = Namespace(fa=str(fa), json=False)

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "Number of sequences" in output
        assert "Total length" in output
        assert "N50" in output
