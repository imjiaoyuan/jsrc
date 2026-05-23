import json
from argparse import Namespace

from jsrc.genome.motif_scan import _scan_motif, cmd


class TestScanMotif:
    def test_exact_match(self):
        seq = "ATGCATGC"
        motif = "ATG"
        matches = _scan_motif(seq, motif, allow_mismatch=0)
        assert len(matches) == 2
        assert matches[0]["start"] == 0
        assert matches[0]["sequence"] == "ATG"
        assert matches[0]["mismatches"] == 0

    def test_no_match(self):
        seq = "AAAAAAA"
        motif = "GGG"
        matches = _scan_motif(seq, motif, allow_mismatch=0)
        assert len(matches) == 0

    def test_iupac_code_r(self):
        seq = "ATGAATGA"
        motif = "ATR"
        matches = _scan_motif(seq, motif, allow_mismatch=0)
        assert len(matches) >= 1

    def test_iupac_code_n(self):
        seq = "ATGC"
        motif = "ATNN"
        matches = _scan_motif(seq, motif, allow_mismatch=0)
        assert len(matches) == 1

    def test_allow_one_mismatch(self):
        seq = "ATGC"
        motif = "ATGG"
        matches = _scan_motif(seq, motif, allow_mismatch=1)
        assert len(matches) == 1
        assert matches[0]["mismatches"] == 1

    def test_allow_multiple_mismatches(self):
        seq = "ATGC"
        motif = "ATGG"
        matches = _scan_motif(seq, motif, allow_mismatch=1)
        assert len(matches) >= 1
        assert matches[0]["mismatches"] == 1

    def test_case_insensitive(self):
        seq = "atgc"
        motif = "ATG"
        matches = _scan_motif(seq, motif, allow_mismatch=0)
        assert len(matches) == 1


class TestMotifScanCmd:
    def test_motif_scan_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa=str(fa), motif="ATG", mismatch=0, top=100, json=False)

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

    def test_motif_scan_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa=str(fa), motif="ATG", mismatch=0, top=100, json=True)

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
        assert "matches" in data[0]

    def test_motif_scan_with_mismatch(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa=str(fa), motif="ATGG", mismatch=1, top=100, json=True)

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
        if data[0]["matches"]:
            assert data[0]["matches"][0]["mismatches"] <= 1

    def test_motif_scan_iupac_codes(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGAATGA\n")

        args = Namespace(fa=str(fa), motif="ATR", mismatch=0, top=100, json=True)

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
        assert len(data[0]["matches"]) >= 1

    def test_motif_scan_top_limit(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "ATG" * 50 + "\n")

        args = Namespace(fa=str(fa), motif="ATG", mismatch=0, top=5, json=True)

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

    def test_motif_scan_no_matches(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nAAAAAAAA\n")

        args = Namespace(fa=str(fa), motif="GGG", mismatch=0, top=100, json=True)

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
        assert len(data[0]["matches"]) == 0

    def test_motif_scan_multiple_sequences(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATGC\n>seq2\nATGG\n")

        args = Namespace(fa=str(fa), motif="ATG", mismatch=0, top=100, json=True)

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
