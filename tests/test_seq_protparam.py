import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.seq.protparam import _aliphatic_index, cmd


class TestAliphaticIndex:
    def test_empty_sequence(self):
        assert _aliphatic_index("") == 0.0

    def test_known_value(self):
        ai = _aliphatic_index("AVIL" * 10)
        assert ai > 50.0

    def test_non_aliphatic(self):
        ai = _aliphatic_index("GGGGGGGGGG")
        assert ai == pytest.approx(0.0, abs=0.1)


class TestCmd:
    def test_basic_output(self, tmp_path, capsys):
        fa = tmp_path / "prots.fa"
        fa.write_text(">p1\nAVILGGGG\n>p2\nMKTWQF\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False, ph=None)
        cmd(args)
        out = capsys.readouterr().out
        assert "p1" in out
        assert "p2" in out
        assert "molecular_weight" in out or "mw" in out.lower()

    def test_json_output(self, tmp_path, capsys):
        fa = tmp_path / "prots.fa"
        fa.write_text(">p1\nAVILGGGG\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=True, ph=None)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["id"] == "p1"
        assert data[0]["length"] == 8
        assert "molecular_weight" in data[0]
        assert "isoelectric_point" in data[0]
        assert "gravy" in data[0]

    def test_charge_at_ph(self, tmp_path, capsys):
        fa = tmp_path / "prots.fa"
        fa.write_text(">p1\nAVILGGGG\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=True, ph=7.0)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "charge_at_pH" in data[0]

    def test_empty_fasta_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("", encoding="utf-8")
        args = Namespace(fa=str(fa), json=False, ph=None)
        with pytest.raises(DataFormatError):
            cmd(args)

    def test_lowercase_normalized(self, tmp_path, capsys):
        fa = tmp_path / "prots.fa"
        fa.write_text(">p1\navilgggg\n", encoding="utf-8")
        args = Namespace(fa=str(fa), json=True, ph=None)
        cmd(args)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data[0]["length"] == 8
