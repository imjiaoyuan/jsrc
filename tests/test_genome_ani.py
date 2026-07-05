import json
from argparse import Namespace

import pytest

from jsrc.core import DataFormatError, ValidationError
from jsrc.genome.ani import (
    _cosine_similarity,
    _jaccard_similarity,
    _kmer_profile,
    _mash_distance,
    cmd,
)


class TestKmerProfile:
    def test_basic_kmer_profile(self):
        seq = "ATGC"
        profile = _kmer_profile(seq, k=2)
        assert profile["AT"] == 1
        assert profile["TG"] == 1
        assert profile["GC"] == 1

    def test_kmer_profile_overlapping(self):
        seq = "AAAA"
        profile = _kmer_profile(seq, k=2)
        assert profile["AA"] == 3

    def test_kmer_profile_invalid_bases(self):
        seq = "ATNGC"
        profile = _kmer_profile(seq, k=2)
        assert "TN" not in profile
        assert "NG" not in profile


class TestSimilarityFunctions:
    def test_jaccard_similarity_identical(self):
        from collections import Counter

        profile1 = Counter({"AT": 2, "TG": 1})
        profile2 = Counter({"AT": 2, "TG": 1})
        sim = _jaccard_similarity(profile1, profile2)
        assert sim == 1.0

    def test_jaccard_similarity_different(self):
        from collections import Counter

        profile1 = Counter({"AT": 2})
        profile2 = Counter({"GC": 2})
        sim = _jaccard_similarity(profile1, profile2)
        assert sim == 0.0

    def test_cosine_similarity_identical(self):
        from collections import Counter

        profile1 = Counter({"AT": 2, "TG": 1})
        profile2 = Counter({"AT": 2, "TG": 1})
        sim = _cosine_similarity(profile1, profile2)
        assert abs(sim - 1.0) < 1e-10

    def test_cosine_similarity_different(self):
        from collections import Counter

        profile1 = Counter({"AT": 2})
        profile2 = Counter({"GC": 2})
        sim = _cosine_similarity(profile1, profile2)
        assert sim == 0.0

    def test_mash_distance(self):
        from collections import Counter

        profile1 = Counter({"AT": 2, "TG": 1})
        profile2 = Counter({"AT": 2, "TG": 1})
        dist = _mash_distance(profile1, profile2, k=2)
        assert dist >= 0


class TestAniCmd:
    def test_ani_basic_output(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGCATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=False)

        import io
        import sys

        captured = io.StringIO()
        sys.stdout = captured
        try:
            cmd(args)
        finally:
            sys.stdout = sys.__stdout__

        output = captured.getvalue()
        assert "ANI estimate" in output

    def test_ani_json_output(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGCATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=True)

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
        assert "ani_estimate_percent" in data
        assert "jaccard_similarity" in data
        assert "cosine_similarity" in data
        assert "mash_distance" in data

    def test_ani_identical_genomes(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGCATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGCATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=True)

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
        assert data["ani_estimate_percent"] > 99.0

    def test_ani_different_genomes(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGCATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nGGGGGGGG\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=True)

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
        assert data["ani_estimate_percent"] >= 0

    def test_ani_invalid_k_raises(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=0, json=False)

        with pytest.raises(ValidationError):
            cmd(args)

    def test_ani_empty_file_raises(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text("")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=False)

        with pytest.raises(DataFormatError):
            cmd(args)

    def test_ani_multiple_sequences(self, tmp_path):
        fa1 = tmp_path / "genome1.fa"
        fa1.write_text(">seq1\nATGC\n>seq2\nATGC\n")

        fa2 = tmp_path / "genome2.fa"
        fa2.write_text(">seq1\nATGC\n>seq2\nATGC\n")

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, json=True)

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
        assert data["genome1_length"] == 8
        assert data["genome2_length"] == 8
