import json
from argparse import Namespace

import pytest

from jsrc.genome.gc_skew import _calculate_cumulative_gc_skew, _find_skew_extrema, cmd


class TestGcSkewFunctions:
    def test_calculate_cumulative_gc_skew(self):
        seq = "GGGGCCCC" * 10
        results = _calculate_cumulative_gc_skew(seq, window=20, step=10)
        assert len(results) > 0
        assert "cumulative_gc_skew" in results[0]
        assert "gc_skew" in results[0]

    def test_gc_skew_positive(self):
        seq = "GGGG" * 10
        results = _calculate_cumulative_gc_skew(seq, window=10, step=5)
        assert results[0]["gc_skew"] > 0

    def test_gc_skew_negative(self):
        seq = "CCCC" * 10
        results = _calculate_cumulative_gc_skew(seq, window=10, step=5)
        assert results[0]["gc_skew"] < 0

    def test_gc_skew_zero_gc_content(self):
        seq = "AAAA" * 10
        results = _calculate_cumulative_gc_skew(seq, window=10, step=5)
        assert results[0]["gc_skew"] == 0.0

    def test_find_skew_extrema(self):
        data = [
            {"position": 1, "cumulative_gc_skew": 0.5},
            {"position": 2, "cumulative_gc_skew": -0.5},
            {"position": 3, "cumulative_gc_skew": 1.0},
        ]
        min_point, max_point = _find_skew_extrema(data)
        assert min_point["cumulative_gc_skew"] == -0.5
        assert max_point["cumulative_gc_skew"] == 1.0

    def test_find_skew_extrema_empty(self):
        min_point, max_point = _find_skew_extrema([])
        assert min_point is None
        assert max_point is None


class TestGcSkewCmd:
    def test_gc_skew_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")

        args = Namespace(fa=str(fa), id=None, window=100, step=50, head=20, json=False)

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
        assert "replication origin" in output.lower()

    def test_gc_skew_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")

        args = Namespace(fa=str(fa), id=None, window=100, step=50, head=20, json=True)

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
        assert data["sequence_id"] == "seq1"
        assert "skew_data" in data
        assert "min_skew_position" in data
        assert "max_skew_position" in data

    def test_gc_skew_specific_sequence(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGG" * 50 + "\n>seq2\n" + "CCCC" * 50 + "\n")

        args = Namespace(fa=str(fa), id="seq2", window=50, step=25, head=10, json=True)

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
        assert data["sequence_id"] == "seq2"

    def test_gc_skew_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")

        args = Namespace(fa=str(fa), id=None, window=100, step=50, head=20, json=False)

        with pytest.raises(SystemExit):
            cmd(args)

    def test_gc_skew_sequence_not_found_raises(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGG" * 50 + "\n")

        args = Namespace(
            fa=str(fa), id="seq999", window=100, step=50, head=20, json=False
        )

        with pytest.raises(SystemExit):
            cmd(args)

    def test_gc_skew_head_limit(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")

        args = Namespace(fa=str(fa), id=None, window=50, step=10, head=5, json=True)

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
        assert len(data["skew_data"]) == 5

    def test_gc_skew_all_data_points(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 50 + "\n")

        args = Namespace(fa=str(fa), id=None, window=50, step=10, head=0, json=True)

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
        assert len(data["skew_data"]) == data["data_points"]
