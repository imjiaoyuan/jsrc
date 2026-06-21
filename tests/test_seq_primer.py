import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.seq.primer import (
    _gc_clamp,
    _has_hairpin,
    _tm_nearest_neighbor,
    _tm_wallace,
    cmd,
)


class TestTmWallace:
    def test_short_primer(self):
        tm = _tm_wallace("ATCG")
        assert tm == 2 * 2 + 4 * 2  # A+T=2, G+C=2

    def test_long_primer(self):
        tm = _tm_wallace("GCCGGCCGGCCGGCCG")
        # Wallace rule for >= 14 bp
        assert tm > 50

    def test_mixed_case(self):
        tm_upper = _tm_wallace("ATCGATCGATCGATCG")
        tm_lower = _tm_wallace("atcgatcgatcgatcg")
        assert tm_upper == tm_lower

    def test_with_uracil(self):
        tm = _tm_wallace("AUCGAUCG")
        tm_t = _tm_wallace("ATCGATCG")
        assert tm == tm_t


class TestTmNearestNeighbor:
    def test_basic_calculation(self):
        tm = _tm_nearest_neighbor("ATCGATCGATCG", conc_nm=250.0)
        assert 30.0 < tm < 80.0

    def test_higher_concentration_yields_higher_tm(self):
        tm_low = _tm_nearest_neighbor("ATCGATCGATCG", conc_nm=50.0)
        tm_high = _tm_nearest_neighbor("ATCGATCGATCG", conc_nm=500.0)
        assert tm_low < tm_high


class TestHairpin:
    def test_no_hairpin(self):
        assert not _has_hairpin("AAAAAAAAAAAAAAAA")

    def test_simple_hairpin(self):
        # ATCG ... loop ... CGAT
        seq = "ATCG" + "AAAA" + "CGAT"
        assert _has_hairpin(seq, min_stem=3, loop=4)

    def test_short_sequence_no_hairpin(self):
        assert not _has_hairpin("ATCG", min_stem=3, loop=4)


class TestGcClamp:
    def test_gc_end(self):
        assert _gc_clamp("ATCGATCG")

    def test_at_end(self):
        assert not _gc_clamp("ATCGATCA")

    def test_custom_n(self):
        assert _gc_clamp("ATCG", n=1)


class TestCmd:
    def test_basic_output(self, tmp_path, capsys):
        fa = tmp_path / "primers.fa"
        fa.write_text(">p1\nATCGATCGATCG\n>p2\nGGCCGGCCGGCC\n", encoding="utf-8")
        args = Namespace(fa=str(fa), conc=250.0, json=False)
        cmd(args)
        out = capsys.readouterr().out
        assert "p1" in out
        assert "p2" in out
        assert "tm_wallace" in out
        assert "tm_nn" in out
        assert "gc_clamp" in out
        assert "hairpin_risk" in out

    def test_json_output(self, tmp_path, capsys):
        fa = tmp_path / "primers.fa"
        fa.write_text(">p1\nATCGATCGATCG\n", encoding="utf-8")
        args = Namespace(fa=str(fa), conc=250.0, json=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data[0]["id"] == "p1"
        assert "gc_percent" in data[0]
        assert "tm_nearest_neighbor" in data[0]

    def test_custom_concentration(self, tmp_path, capsys):
        fa = tmp_path / "primers.fa"
        fa.write_text(">p1\nATCGATCGATCG\n", encoding="utf-8")
        args = Namespace(fa=str(fa), conc=50.0, json=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        tm_50 = data[0]["tm_nearest_neighbor"]

        args = Namespace(fa=str(fa), conc=500.0, json=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        tm_500 = data[0]["tm_nearest_neighbor"]
        assert tm_50 < tm_500

    def test_empty_fasta_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("", encoding="utf-8")
        args = Namespace(fa=str(fa), conc=250.0, json=False)
        with pytest.raises(DataFormatError):
            cmd(args)

    def test_gc_content(self, tmp_path, capsys):
        fa = tmp_path / "primers.fa"
        fa.write_text(">p_gc\nGGCCGGCC\n>p_at\nATATATAT\n", encoding="utf-8")
        args = Namespace(fa=str(fa), conc=250.0, json=True)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        gc_primer = next(r for r in data if r["id"] == "p_gc")
        at_primer = next(r for r in data if r["id"] == "p_at")
        assert gc_primer["gc_percent"] > 90
        assert at_primer["gc_percent"] < 10
