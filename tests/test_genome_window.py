import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.genome.window import cmd


def test_seq_window_json_output(tmp_path, capsys):
    fasta = tmp_path / "a.fa"
    fasta.write_text(">s1\nATGCGCGTAA\n", encoding="utf-8")
    args = Namespace(
        fa=str(fasta), id=None, w=4, s=2, head=3, json=True, cumulative=False
    )
    cmd(args)
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["sequence_id"] == "s1"
    assert payload["window_count"] >= 1
    assert "windows_head" in payload


def test_seq_window_uses_longest_record_by_default(tmp_path, capsys):
    fasta = tmp_path / "mix.fa"
    fasta.write_text(">s1\nATGC\n>s2\nATGCATGCAT\n", encoding="utf-8")
    args = Namespace(
        fa=str(fasta), id=None, w=4, s=2, head=2, json=True, cumulative=False
    )
    cmd(args)
    payload = json.loads(capsys.readouterr().out)
    assert payload["sequence_id"] == "s2"
    assert payload["sequence_length"] == 10


class TestCumulativeGcSkew:
    """Cumulative GC skew + replication-origin prediction (migrated from `genome gc-skew`)."""

    def test_helper_runs(self):
        from jsrc.genome.window import _calculate_cumulative_gc_skew

        results = _calculate_cumulative_gc_skew("GGGGCCCC" * 10, window=20, step=10)
        assert len(results) > 0
        assert "cumulative_gc_skew" in results[0]
        assert "gc_skew" in results[0]

    def test_helper_positive(self):
        from jsrc.genome.window import _calculate_cumulative_gc_skew

        results = _calculate_cumulative_gc_skew("GGGG" * 10, window=10, step=5)
        assert results[0]["gc_skew"] > 0

    def test_helper_negative(self):
        from jsrc.genome.window import _calculate_cumulative_gc_skew

        results = _calculate_cumulative_gc_skew("CCCC" * 10, window=10, step=5)
        assert results[0]["gc_skew"] < 0

    def test_helper_zero_gc(self):
        from jsrc.genome.window import _calculate_cumulative_gc_skew

        results = _calculate_cumulative_gc_skew("AAAA" * 10, window=10, step=5)
        assert results[0]["gc_skew"] == 0.0

    def test_find_extrema(self):
        from jsrc.genome.window import _find_skew_extrema

        data = [
            {"position": 1, "cumulative_gc_skew": 0.5},
            {"position": 2, "cumulative_gc_skew": -0.5},
            {"position": 3, "cumulative_gc_skew": 1.0},
        ]
        mn, mx = _find_skew_extrema(data)
        assert mn["cumulative_gc_skew"] == -0.5
        assert mx["cumulative_gc_skew"] == 1.0

    def test_find_extrema_empty(self):
        from jsrc.genome.window import _find_skew_extrema

        mn, mx = _find_skew_extrema([])
        assert mn is None
        assert mx is None

    def test_cumulative_text_origin(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")
        cmd(
            Namespace(
                fa=str(fa), id=None, w=100, s=50, head=20, json=False, cumulative=True
            )
        )
        assert "replication origin" in capsys.readouterr().out.lower()

    def test_cumulative_json_schema(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")
        cmd(
            Namespace(
                fa=str(fa), id=None, w=100, s=50, head=20, json=True, cumulative=True
            )
        )
        data = json.loads(capsys.readouterr().out)
        assert data["sequence_id"] == "seq1"
        assert "skew_data" in data
        assert "min_skew_position" in data
        assert "max_skew_position" in data

    def test_cumulative_id_select(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGG" * 50 + "\n>seq2\n" + "CCCC" * 50 + "\n")
        cmd(
            Namespace(
                fa=str(fa), id="seq2", w=50, s=25, head=10, json=True, cumulative=True
            )
        )
        assert json.loads(capsys.readouterr().out)["sequence_id"] == "seq2"

    def test_cumulative_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")
        with pytest.raises(DataFormatError):
            cmd(
                Namespace(
                    fa=str(fa),
                    id=None,
                    w=100,
                    s=50,
                    head=20,
                    json=False,
                    cumulative=True,
                )
            )

    def test_cumulative_id_not_found_raises(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGG" * 50 + "\n")
        with pytest.raises(DataFormatError):
            cmd(
                Namespace(
                    fa=str(fa),
                    id="seq999",
                    w=100,
                    s=50,
                    head=20,
                    json=False,
                    cumulative=True,
                )
            )

    def test_cumulative_head_limit(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 100 + "\n")
        cmd(
            Namespace(
                fa=str(fa), id=None, w=50, s=10, head=5, json=True, cumulative=True
            )
        )
        assert len(json.loads(capsys.readouterr().out)["skew_data"]) == 5

    def test_cumulative_all_points(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "GGGGCCCC" * 50 + "\n")
        cmd(
            Namespace(
                fa=str(fa), id=None, w=50, s=10, head=0, json=True, cumulative=True
            )
        )
        data = json.loads(capsys.readouterr().out)
        assert len(data["skew_data"]) == data["data_points"]
