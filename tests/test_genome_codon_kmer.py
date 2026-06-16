import json
import logging
from argparse import Namespace

import pytest

from jsrc.core import ValidationError
from jsrc.genome.codon import cmd as codon_cmd
from jsrc.seq.kmer import cmd as kmer_cmd


class TestCodonUsage:
    def test_codon_basic(self, tmp_path, capsys, caplog):
        caplog.set_level(logging.INFO)
        fa = tmp_path / "cds.fa"
        fa.write_text(">g1\nATGGCCACTTAA\n", encoding="utf-8")

        args = Namespace(fa=str(fa), top=20, json=False, cai=None, enc=False)
        codon_cmd(args)

        captured = capsys.readouterr()
        assert "total_codons" in caplog.text
        assert "codon\tcount\tfreq\trscu" in captured.out

    def test_codon_json(self, tmp_path, capsys):
        fa = tmp_path / "cds.fa"
        fa.write_text(">g1\nATGGCCACTTAA\n", encoding="utf-8")

        args = Namespace(fa=str(fa), top=20, json=True, cai=None, enc=False)
        codon_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["total_codons"] == 3
        assert len(payload["top_codons"]) == 3

    def test_codon_empty(self, tmp_path, capsys):
        fa = tmp_path / "empty.fa"
        fa.write_text(">g1\nNNNNNN\n", encoding="utf-8")

        args = Namespace(fa=str(fa), top=20, json=True, cai=None, enc=False)
        codon_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["total_codons"] == 0


class TestKmer:
    def test_kmer_single_file(self, tmp_path, capsys):
        fa = tmp_path / "seq.fa"
        fa.write_text(">s1\nATGCATGC\n", encoding="utf-8")

        args = Namespace(fa=[str(fa)], k=3, top=10, json=False)
        kmer_cmd(args)

        out = capsys.readouterr().out
        assert "total_kmers" in out
        assert "kmer\tcount\tfreq" in out

    def test_kmer_single_json(self, tmp_path, capsys):
        fa = tmp_path / "seq.fa"
        fa.write_text(">s1\nATGCATGC\n", encoding="utf-8")

        args = Namespace(fa=[str(fa)], k=3, top=10, json=True)
        kmer_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["k"] == 3
        assert payload["total_kmers"] == 6
        assert len(payload["top_kmers"]) == 4

    def test_kmer_multiple_files_distance(self, tmp_path, capsys):
        fa1 = tmp_path / "a.fa"
        fa1.write_text(">a\nATGCATGC\n", encoding="utf-8")
        fa2 = tmp_path / "b.fa"
        fa2.write_text(">b\nATGCGGCC\n", encoding="utf-8")

        args = Namespace(fa=[str(fa1), str(fa2)], k=3, top=10, json=True)
        kmer_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert "cosine_distance_matrix" in payload
        assert payload["samples"] == [str(fa1), str(fa2)]

        assert payload["cosine_distance_matrix"][0][0] == pytest.approx(0.0, abs=1e-10)
        assert payload["cosine_distance_matrix"][1][1] == pytest.approx(0.0, abs=1e-10)

    def test_kmer_invalid_k_raises(self, tmp_path):
        fa = tmp_path / "seq.fa"
        fa.write_text(">s1\nATGC\n", encoding="utf-8")

        args = Namespace(fa=[str(fa)], k=0, top=10, json=False)
        with pytest.raises(ValidationError):
            kmer_cmd(args)
