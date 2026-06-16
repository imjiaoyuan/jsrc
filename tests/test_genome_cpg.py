import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.genome.cpg import _cpg_islands, cmd


class TestCpgIslands:
    def test_basic_cpg_island(self):
        seq = "CG" * 100
        islands = _cpg_islands(
            seq, window=50, step=10, min_len=100, min_gc=0.5, min_oe=0.6
        )
        assert len(islands) >= 1
        assert islands[0]["length"] >= 100
        assert islands[0]["gc_percent"] >= 50.0

    def test_no_cpg_island(self):
        seq = "AT" * 100
        islands = _cpg_islands(
            seq, window=50, step=10, min_len=100, min_gc=0.5, min_oe=0.6
        )
        assert len(islands) == 0

    def test_min_length_filter(self):
        seq = "CG" * 30
        islands = _cpg_islands(
            seq, window=20, step=5, min_len=100, min_gc=0.5, min_oe=0.6
        )
        assert len(islands) == 0

    def test_gc_content_threshold(self):
        seq = "CGAT" * 50
        islands = _cpg_islands(
            seq, window=50, step=10, min_len=50, min_gc=0.8, min_oe=0.6
        )
        assert len(islands) == 0

    def test_obs_exp_ratio(self):
        seq = "CCGG" * 50
        islands = _cpg_islands(
            seq, window=50, step=10, min_len=50, min_gc=0.5, min_oe=0.6
        )
        assert len(islands) >= 1
        assert islands[0]["obs_exp_cpg"] >= 0.6

    def test_rna_sequence_converted(self):
        seq = "CG" * 100
        seq_rna = seq.replace("T", "U")
        islands = _cpg_islands(
            seq_rna, window=50, step=10, min_len=100, min_gc=0.5, min_oe=0.6
        )
        assert len(islands) >= 1


class TestCpgCmd:
    def test_cpg_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "CG" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            min_len=100,
            min_gc=50.0,
            min_oe=0.6,
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
        assert "seq1" in output or "seq_id" in output

    def test_cpg_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "CG" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            min_len=100,
            min_gc=50.0,
            min_oe=0.6,
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
        if len(data) > 0:
            assert data[0]["seq_id"] == "seq1"
            assert "gc_percent" in data[0]
            assert "obs_exp_cpg" in data[0]

    def test_cpg_no_islands_found(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "AT" * 100 + "\n")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            min_len=100,
            min_gc=50.0,
            min_oe=0.6,
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
        assert len(data) == 0

    def test_cpg_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")

        args = Namespace(
            fa=str(fa),
            window=50,
            step=10,
            min_len=100,
            min_gc=50.0,
            min_oe=0.6,
            json=False,
        )

        with pytest.raises(DataFormatError):
            cmd(args)
