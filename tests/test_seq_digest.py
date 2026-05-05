import json
import logging
from argparse import Namespace

from jsrc.seq.digest import _calc_fragments, cmd


class TestCalcFragments:
    def test_no_cuts_linear(self):
        assert _calc_fragments([], 100, circular=False) == [100]

    def test_no_cuts_circular(self):
        assert _calc_fragments([], 100, circular=True) == [100]

    def test_single_cut_linear(self):
        # 100 bp, cut at 40 → fragments: 40 bp, 60 bp
        result = _calc_fragments([40], 100, circular=False)
        assert result == [60, 40]

    def test_single_cut_circular(self):
        # 100 bp, cut at 40 → one circular fragment of 100 bp
        result = _calc_fragments([40], 100, circular=True)
        assert result == [100]

    def test_two_cuts_linear(self):
        result = _calc_fragments([20, 60], 100, circular=False)
        # boundaries: [0, 20, 60, 100] → fragments: 20, 40, 40
        assert result == [40, 40, 20]

    def test_two_cuts_circular(self):
        # positions [20, 60], length 100
        # fragments: 20-0=20 (but wait, in circular, [0] not added)
        # i=0: start=20, end=60 → 40
        # i=1: start=60, end=20+100=120 → 60
        # sorted: [60, 40]
        result = _calc_fragments([20, 60], 100, circular=True)
        assert result == [60, 40]

    def test_duplicate_cuts(self):
        # Duplicate positions should be deduplicated
        result = _calc_fragments([30, 30, 70], 100, circular=False)
        # boundaries: [0, 30, 70, 100] → fragments: 30, 40, 30
        assert result == [40, 30, 30]


class TestDigestCmd:
    def test_digest_basic_linear(self, tmp_path, capsys, caplog):
        caplog.set_level(logging.INFO)
        fa = tmp_path / "seq.fa"
        # EcoRI site: GAATTC
        fa.write_text(">test\nAAAAAAGAATTCCCCCC\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI",
            circular=False,
            min_size=0,
            json=False,
        )
        cmd(args)

        out = capsys.readouterr().out
        assert "Digest of test" in out
        assert "bp" in out
        assert "linear" in caplog.text

    def test_digest_json(self, tmp_path, capsys):
        fa = tmp_path / "seq.fa"
        fa.write_text(">test\nAAAAAAGAATTCCCCCC\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI",
            circular=False,
            min_size=0,
            json=True,
        )
        cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["sequence_id"] == "test"
        assert payload["sequence_length"] == 17
        assert payload["mode"] == "linear"
        assert payload["enzymes"] == ["EcoRI"]
        assert "fragment_sizes" in payload

    def test_digest_circular(self, tmp_path, capsys, caplog):
        caplog.set_level(logging.INFO)
        fa = tmp_path / "plasmid.fa"
        # EcoRI site: GAATTC
        fa.write_text(">plasmid\nGAATTCAAAAAAGCTTCCCCC\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI,HindIII",
            circular=True,
            min_size=0,
            json=True,
        )
        cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["mode"] == "circular"
        assert len(payload["fragment_sizes"]) == 2  # 2 cuts → 2 fragments
        assert "circular" in caplog.text

    def test_digest_min_size(self, tmp_path, capsys, caplog):
        caplog.set_level(logging.INFO)
        fa = tmp_path / "seq.fa"
        fa.write_text(">test\nAAGCTTAAAAAAGAATTC\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI,HindIII",
            circular=False,
            min_size=4,
            json=True,
        )
        cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert "filtered_fragment_sizes" in payload
        assert all(s >= 4 for s in payload["filtered_fragment_sizes"])

    def test_no_enzymes_raises(self, tmp_path):
        fa = tmp_path / "seq.fa"
        fa.write_text(">t\nATGC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), enzymes="", circular=False, min_size=0, json=False)
        try:
            cmd(args)
            assert False, "Should have raised"
        except SystemExit:
            pass

    def test_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("", encoding="utf-8")

        args = Namespace(
            fa=str(fa), enzymes="EcoRI", circular=False, min_size=0, json=False
        )
        try:
            cmd(args)
            assert False, "Should have raised"
        except SystemExit:
            pass

    def test_unrecognized_enzyme_warns(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        fa = tmp_path / "seq.fa"
        fa.write_text(">t\nATGCATGC\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI,FakeEnzyme",
            circular=False,
            min_size=0,
            json=True,
        )
        cmd(args)

        assert "Unrecognized enzymes" in caplog.text
        assert "FakeEnzyme" in caplog.text

    def test_no_cut_sites(self, tmp_path, capsys):
        fa = tmp_path / "seq.fa"
        fa.write_text(">t\nAAAAAAAAAA\n", encoding="utf-8")

        args = Namespace(
            fa=str(fa),
            enzymes="EcoRI",
            circular=False,
            min_size=0,
            json=True,
        )
        cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["total_fragments"] == 1
        assert payload["fragment_sizes"] == [10]
