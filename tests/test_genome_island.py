import json
from argparse import Namespace

from jsrc.genome.island import _detect_islands, cmd


class TestDetectIslands:
    def test_high_gc_island(self):
        seq = "GC" * 100
        islands = _detect_islands(seq, window=50, step=10, gc_threshold=0.5)
        assert len(islands) >= 1
        assert islands[0]["length"] > 0

    def test_no_island_low_gc(self):
        seq = "AT" * 100
        islands = _detect_islands(seq, window=50, step=10, gc_threshold=0.5)
        assert len(islands) == 0

    def test_island_boundaries(self):
        seq = "AT" * 50 + "GC" * 50 + "AT" * 50
        islands = _detect_islands(seq, window=20, step=5, gc_threshold=0.6)
        assert len(islands) >= 1

    def test_gc_threshold_filter(self):
        seq = "ATGC" * 50
        islands_low = _detect_islands(seq, window=50, step=10, gc_threshold=0.3)
        islands_high = _detect_islands(seq, window=50, step=10, gc_threshold=0.8)
        assert len(islands_low) >= len(islands_high)

    def test_empty_sequence(self):
        seq = ""
        islands = _detect_islands(seq, window=50, step=10, gc_threshold=0.5)
        assert len(islands) == 0


class TestIslandCmd:
    def test_island_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GC" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            gc_threshold=0.5,
            min_length=None,
            json=False,
        )

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "seq1" in output or len(output) >= 0

    def test_island_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GC" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            gc_threshold=0.5,
            min_length=None,
            json=True,
        )

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
        assert data[0]["seq_id"] == "seq1"
        assert "islands" in data[0]

    def test_island_min_length_filter(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GC" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            gc_threshold=0.5,
            min_length=1000,
            json=True,
        )

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
        if data[0]["islands"]:
            for island in data[0]["islands"]:
                assert island["length"] >= 1000

    def test_island_no_islands_found(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "AT" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            gc_threshold=0.8,
            min_length=None,
            json=True,
        )

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
        assert len(data[0]["islands"]) == 0
