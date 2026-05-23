import json
from argparse import Namespace

import pytest

from jsrc.genome.repeat import _find_repeats, cmd


class TestFindRepeats:
    def test_simple_dinucleotide_repeat(self):
        seq = "ATATATATAT"
        repeats = _find_repeats(seq, min_unit=2, max_unit=2, min_reps=3)
        assert len(repeats) == 1
        assert repeats[0]["unit"] == "AT"
        assert repeats[0]["unit_len"] == 2
        assert repeats[0]["repeats"] == 5
        assert repeats[0]["total_len"] == 10

    def test_trinucleotide_repeat(self):
        seq = "CAGCAGCAGCAG"
        repeats = _find_repeats(seq, min_unit=3, max_unit=3, min_reps=3)
        assert len(repeats) == 1
        assert repeats[0]["unit"] == "CAG"
        assert repeats[0]["repeats"] == 4

    def test_min_reps_filter(self):
        seq = "ATATAT"
        repeats = _find_repeats(seq, min_unit=2, max_unit=2, min_reps=4)
        assert len(repeats) == 0

    def test_mononucleotide_excluded(self):
        seq = "AAAAAAA"
        repeats = _find_repeats(seq, min_unit=2, max_unit=2, min_reps=3)
        assert len(repeats) == 0

    def test_mononucleotide_included(self):
        seq = "AAAAAAA"
        repeats = _find_repeats(seq, min_unit=1, max_unit=1, min_reps=5)
        assert len(repeats) == 1
        assert repeats[0]["unit"] == "A"
        assert repeats[0]["repeats"] == 7

    def test_multiple_repeats(self):
        seq = "ATATATATGCGCGCGC"
        repeats = _find_repeats(seq, min_unit=2, max_unit=2, min_reps=3)
        assert len(repeats) == 2
        assert repeats[0]["start"] < repeats[1]["start"]

    def test_no_repeats(self):
        seq = "ATCGATCGATCG"
        repeats = _find_repeats(seq, min_unit=2, max_unit=2, min_reps=3)
        assert len(repeats) == 0

    def test_rna_sequence_converted(self):
        seq = "AUGAUGAUGAUG"
        repeats = _find_repeats(seq, min_unit=3, max_unit=3, min_reps=3)
        assert len(repeats) == 1
        assert repeats[0]["unit"] == "ATG"

    def test_range_of_unit_lengths(self):
        seq = "ATATATATAT"
        repeats = _find_repeats(seq, min_unit=2, max_unit=4, min_reps=3)
        assert any(r["unit"] == "AT" and r["repeats"] == 5 for r in repeats)


class TestRepeatCmd:
    def test_repeat_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATATATATAT\n")

        args = Namespace(fa=str(fa), min_unit=2, max_unit=2, min_reps=3, json=False)

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
        assert "seq_id" in output

    def test_repeat_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATATATATAT\n")

        args = Namespace(fa=str(fa), min_unit=2, max_unit=2, min_reps=3, json=True)

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
        assert data[0]["unit"] == "AT"

    def test_repeat_multiple_sequences(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATATATATAT\n>seq2\nGCGCGCGC\n")

        args = Namespace(fa=str(fa), min_unit=2, max_unit=2, min_reps=3, json=True)

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
        assert len(data) == 2
        seq_ids = [r["seq_id"] for r in data]
        assert "seq1" in seq_ids
        assert "seq2" in seq_ids

    def test_repeat_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")

        args = Namespace(fa=str(fa), min_unit=2, max_unit=2, min_reps=3, json=False)

        with pytest.raises(SystemExit):
            cmd(args)
