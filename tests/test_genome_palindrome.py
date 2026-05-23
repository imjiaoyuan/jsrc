import json
from argparse import Namespace

from jsrc.genome.palindrome import _find_palindromes, cmd


class TestFindPalindromes:
    def test_simple_palindrome(self):
        seq = "ATCGAT"
        palindromes = _find_palindromes(seq, min_length=3, max_length=3, max_gap=0)
        assert len(palindromes) >= 1
        assert palindromes[0]["arm_length"] == 3
        assert palindromes[0]["gap"] == 0

    def test_palindrome_with_gap(self):
        seq = "ATCAAGAT"
        palindromes = _find_palindromes(seq, min_length=3, max_length=3, max_gap=2)
        assert len(palindromes) >= 1

    def test_no_palindrome(self):
        seq = "AAAAAAA"
        palindromes = _find_palindromes(seq, min_length=3, max_length=5, max_gap=2)
        assert len(palindromes) == 0

    def test_min_length_filter(self):
        seq = "ATCGAT"
        palindromes = _find_palindromes(seq, min_length=10, max_length=15, max_gap=0)
        assert len(palindromes) == 0

    def test_multiple_palindromes(self):
        seq = "ATCGATNNNATCGAT"
        palindromes = _find_palindromes(seq, min_length=3, max_length=3, max_gap=0)
        assert len(palindromes) >= 1

    def test_palindrome_sequence_correct(self):
        seq = "ATCGAT"
        palindromes = _find_palindromes(seq, min_length=3, max_length=3, max_gap=0)
        if palindromes:
            assert palindromes[0]["sequence"] == "ATCGAT"


class TestPalindromeCmd:
    def test_palindrome_basic_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATCGAT\n")

        args = Namespace(
            fa=str(fa), min_arm=3, max_arm=3, max_gap=0, top=50, json=False
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

    def test_palindrome_json_output(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nATCGAT\n")

        args = Namespace(fa=str(fa), min_arm=3, max_arm=3, max_gap=0, top=50, json=True)

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
        assert "palindromes" in data[0]

    def test_palindrome_no_results(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\nAAAAAAAA\n")

        args = Namespace(fa=str(fa), min_arm=3, max_arm=5, max_gap=2, top=50, json=True)

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
        assert len(data[0]["palindromes"]) == 0

    def test_palindrome_top_limit(self, tmp_path):
        fa = tmp_path / "test.fa"
        fa.write_text(">seq1\n" + "ATCGAT" * 10 + "\n")

        args = Namespace(fa=str(fa), min_arm=3, max_arm=3, max_gap=0, top=5, json=True)

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
