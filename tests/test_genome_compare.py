import json
from argparse import Namespace

import pytest


class TestCompareCmd:
    def test_compare_requires_edlib(self, tmp_path):
        """Test that compare command requires edlib package"""
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=False)

        from jsrc.genome.compare import cmd

        try:
            import edlib  # noqa: F401

            edlib_available = True
        except ImportError:
            edlib_available = False

        if not edlib_available:
            with pytest.raises(SystemExit):
                cmd(args)
        else:
            cmd(args)

    @pytest.mark.skipif(
        not pytest.importorskip("edlib", reason="edlib not installed"), reason=""
    )
    def test_compare_identical_genomes(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=True)

        import io
        import sys

        from jsrc.genome.compare import cmd

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        lines = output.strip().split("\n")
        json_output = "\n".join(lines[-1:])
        data = json.loads(json_output)
        assert data["percent_identity"] == 100.0
        assert data["edit_distance"] == 0

    @pytest.mark.skipif(
        not pytest.importorskip("edlib", reason="edlib not installed"), reason=""
    )
    def test_compare_different_genomes(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGG\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=True)

        import io
        import sys

        from jsrc.genome.compare import cmd

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        lines = output.strip().split("\n")
        json_output = "\n".join(lines[-1:])
        data = json.loads(json_output)
        assert data["percent_identity"] < 100.0
        assert data["edit_distance"] > 0

    @pytest.mark.skipif(
        not pytest.importorskip("edlib", reason="edlib not installed"), reason=""
    )
    def test_compare_empty_file_raises(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text("")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=False)

        from jsrc.genome.compare import cmd

        with pytest.raises(SystemExit):
            cmd(args)

    @pytest.mark.skipif(
        not pytest.importorskip("edlib", reason="edlib not installed"), reason=""
    )
    def test_compare_basic_output(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=False)

        import io
        import sys

        from jsrc.genome.compare import cmd

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "Genome 1" in output
        assert "Genome 2" in output
        assert "GENOME COMPARISON STATISTICS" in output

    @pytest.mark.skipif(
        not pytest.importorskip("edlib", reason="edlib not installed"), reason=""
    )
    def test_compare_multiple_sequences(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n>seq2\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n>seq2\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), json=True)

        import io
        import sys

        from jsrc.genome.compare import cmd

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        lines = output.strip().split("\n")
        json_output = "\n".join(lines[-1:])
        data = json.loads(json_output)
        assert data["genome1_length"] == 8
        assert data["genome2_length"] == 8
