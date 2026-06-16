import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError
from jsrc.genome.orf import _find_orfs, cmd


class TestFindOrfs:
    def test_basic_orf_detection(self):
        seq = "ATGAAATAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 1
        assert orfs[0]["start"] == 1
        assert orfs[0]["end"] == 9
        assert orfs[0]["length"] == 9
        assert orfs[0]["frame"] == 1
        assert orfs[0]["strand"] == "+"
        assert orfs[0]["protein"] == "MK"

    def test_orf_with_multiple_codons(self):
        seq = "ATGGCATAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 1
        assert orfs[0]["protein"] == "MA"

    def test_min_length_filter(self):
        seq = "ATGAAATAA"
        orfs = _find_orfs(seq, min_len=10, all_frames=False)
        assert len(orfs) == 0

    def test_all_frames(self):
        seq = "ATGAAATAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=True)
        assert len(orfs) == 1
        assert orfs[0]["frame"] == 1

    def test_multiple_orfs_sorted_by_length(self):
        seq = "ATGAAATAAATGGCAGCATAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 2
        assert orfs[0]["length"] >= orfs[1]["length"]

    def test_no_start_codon(self):
        seq = "AAAAAATAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 0

    def test_no_stop_codon(self):
        seq = "ATGAAAAAAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 0

    def test_rna_sequence_converted(self):
        seq = "AUGAAAUAA"
        orfs = _find_orfs(seq, min_len=9, all_frames=False)
        assert len(orfs) == 1
        assert orfs[0]["protein"] == "MK"


class TestOrfCmd:
    def test_orf_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGGCATAA\n")

        args = Namespace(fa=str(fa), min_len=9, all_frames=False, top=0, json=False)

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

    def test_orf_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGGCATAA\n")

        args = Namespace(fa=str(fa), min_len=9, all_frames=False, top=0, json=True)

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

    def test_orf_top_limit(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAAATAAATGGCATAA\n")

        args = Namespace(fa=str(fa), min_len=9, all_frames=False, top=1, json=True)

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

    def test_orf_no_sequences_raises(self, tmp_path):
        fa = tmp_path / "empty.fa"
        fa.write_text("")

        args = Namespace(fa=str(fa), min_len=100, all_frames=False, top=0, json=False)

        with pytest.raises(DataFormatError):
            cmd(args)
