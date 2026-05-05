import json
import logging
from argparse import Namespace

from jsrc.analyze.motif import cmd as motif_cmd
from jsrc.analyze.msa_consensus import cmd as msa_cmd
from jsrc.analyze.snpindel import cmd as snpindel_cmd
from jsrc.analyze.qc import cmd as qc_cmd


class TestAnalyzeQC:
    def test_qc_fasta_only(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">s1\nATGCGC\n>s2\nGGCC\n", encoding="utf-8")

        args = Namespace(fa=fa, sam=None, fq=None, vcf=None, gs=None, json=False)
        qc_cmd(args)

        out = capsys.readouterr().out
        assert "[assembly]" in out
        assert "contig_count" in out
        assert "gc_percent" in out

    def test_qc_json(self, tmp_path, capsys):
        fa = tmp_path / "test.fa"
        fa.write_text(">s1\nATGCGC\n>s2\nGGCC\n", encoding="utf-8")

        args = Namespace(fa=fa, sam=None, fq=None, vcf=None, gs=None, json=True)
        qc_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert "assembly" in payload
        assert payload["assembly"]["contig_count"] == 2
        assert payload["assembly"]["total_bases"] == 10

    def test_qc_no_input_raises(self):
        args = Namespace(fa=None, sam=None, fq=None, vcf=None, gs=None, json=False)
        try:
            qc_cmd(args)
            assert False, "Should have raised"
        except SystemExit:
            pass

    def test_qc_vcf(self, tmp_path, capsys):
        vcf_file = tmp_path / "vars.vcf"
        vcf_file.write_text(
            "##fileformat=VCFv4.2\n"
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
            "chr1\t10\t.\tA\tG\t.\t.\t.\n"
            "chr1\t30\t.\tAT\tA\t.\t.\t.\n",
            encoding="utf-8",
        )

        args = Namespace(
            fa=None, sam=None, fq=None, vcf=str(vcf_file), gs=None, json=True
        )
        qc_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["variants"]["variant_total"] == 2
        assert payload["variants"]["snp_count"] == 1
        assert payload["variants"]["indel_count"] == 1


class TestAnalyzeMotif:
    def test_motif_basic(self, tmp_path, caplog):
        caplog.set_level(logging.INFO)
        fa = tmp_path / "seqs.fa"
        fa.write_text(">s1\nATGCATGC\n>s2\nATGCGGCC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), o=str(tmp_path), nmotifs=3, minw=3, maxw=4)
        motif_cmd(args)

        assert "Motif analysis complete" in caplog.text

        tsv = tmp_path / "motifs.tsv"
        assert tsv.exists()
        lines = tsv.read_text().strip().split("\n")
        assert lines[0] == "motif\tcount\tlength"
        assert len(lines) > 1


class TestAnalyzeMsaConsensus:
    def test_msa_basic(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(">s1\nATGC\n>s2\nATCC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), json=False)
        msa_cmd(args)

        out = capsys.readouterr().out
        assert "sequence_count\t2" in out
        assert "alignment_length\t4" in out

    def test_msa_json(self, tmp_path, capsys):
        fa = tmp_path / "aln.fa"
        fa.write_text(">s1\nATGC\n>s2\nATCC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), json=True)
        msa_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["sequence_count"] == 2
        assert payload["alignment_length"] == 4
        assert payload["consensus"] == "ATGC"

        assert payload["mean_conservation"] > 0

    def test_msa_fewer_than_two_raises(self, tmp_path):
        fa = tmp_path / "single.fa"
        fa.write_text(">s1\nATGC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), json=False)
        try:
            msa_cmd(args)
            assert False, "Should have raised"
        except SystemExit:
            pass


class TestAnalyzeSnpIndel:
    def test_snpindel_basic(self, tmp_path, capsys):
        fa = tmp_path / "seqs.fa"
        fa.write_text(">s1\nATGCATGC\n>s2\nATGCGGCC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), id1=None, id2=None, json=True)
        snpindel_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["seq1"] == "s1"
        assert payload["seq2"] == "s2"
        assert payload["snp_count"] == 3

    def test_snpindel_with_ids(self, tmp_path, capsys):
        fa = tmp_path / "seqs.fa"
        fa.write_text(">ref\nATGCATGC\n>qry\nATGCGGCC\n", encoding="utf-8")

        args = Namespace(fa=str(fa), id1="ref", id2="qry", json=True)
        snpindel_cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert payload["seq1"] == "ref"
        assert payload["seq2"] == "qry"
