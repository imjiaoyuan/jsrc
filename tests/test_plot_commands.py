from argparse import Namespace

import pytest


class TestPlotGene:
    def test_gene_structure_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tmRNA\t1\t100\t.\t+\t.\tID=mrna1;Parent=gene1;\n"
            "chr1\tsrc\tCDS\t10\t50\t.\t+\t.\tParent=mrna1\n"
            "chr1\tsrc\tCDS\t60\t90\t.\t+\t.\tParent=mrna1\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n", encoding="utf-8")
        out = tmp_path / "gene.png"

        from jsrc.plot.gene import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        cmd(args)

        assert out.exists()
        assert out.stat().st_size > 0

    def test_gene_multiple_ids(self, tmp_path):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tmRNA\t1\t100\t.\t+\t.\tID=mrna1;Parent=gene1;\n"
            "chr1\tsrc\tmRNA\t200\t300\t.\t+\t.\tID=mrna2;Parent=gene2;\n"
            "chr1\tsrc\tCDS\t10\t50\t.\t+\t.\tParent=mrna1\n"
            "chr1\tsrc\tCDS\t210\t290\t.\t+\t.\tParent=mrna2\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\ngene2\n", encoding="utf-8")
        out = tmp_path / "gene.png"

        from jsrc.plot.gene import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        cmd(args)

        assert out.exists()
        assert out.stat().st_size > 0

    def test_gene_empty_ids_handled_gracefully(self, tmp_path, capsys):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tCDS\t1\t10\t.\t+\t.\tParent=gene1;\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene_nonexistent\n", encoding="utf-8")
        out = tmp_path / "gene.png"

        from jsrc.plot.gene import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()


class TestPlotExon:
    def test_exon_structure_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tmRNA\t1\t200\t.\t+\t.\tID=mrna1;Parent=gene1;\n"
            "chr1\tsrc\texon\t1\t50\t.\t+\t.\tParent=mrna1\n"
            "chr1\tsrc\texon\t100\t150\t.\t+\t.\tParent=mrna1\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n", encoding="utf-8")
        out = tmp_path / "exon.png"

        from jsrc.plot.exon import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()


class TestPlotChromosome:
    def test_chromosome_map_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "##sequence-region chr1 1 1000\n"
            "chr1\tsrc\tgene\t100\t500\t.\t+\t.\tID=gene1;\n"
            "chr1\tsrc\tgene\t600\t900\t.\t+\t.\tID=gene2;\n",
            encoding="utf-8",
        )
        out = tmp_path / "chrom.png"

        from jsrc.plot.chromosome import cmd

        args = Namespace(gff=str(gff), ids=None, o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_chromosome_with_id_filter(self, tmp_path, capsys):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tgene\t100\t500\t.\t+\t.\tID=gene1;\n"
            "chr1\tsrc\tgene\t600\t900\t.\t+\t.\tID=gene2;\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n", encoding="utf-8")
        out = tmp_path / "chrom.png"

        from jsrc.plot.chromosome import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_chromosome_filter_no_match_raises(self, tmp_path):
        pytest.importorskip("matplotlib")
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tgene\t100\t500\t.\t+\t.\tID=gene1;\n",
            encoding="utf-8",
        )
        ids = tmp_path / "ids.txt"
        ids.write_text("gene_nonexistent\n", encoding="utf-8")
        out = tmp_path / "chrom.png"

        from jsrc.plot.chromosome import cmd

        args = Namespace(gff=str(gff), ids=str(ids), o=str(out), dpi=72)
        with pytest.raises(SystemExit, match="No matching genes"):
            cmd(args)


class TestPlotDomain:
    def test_domain_architecture_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        tsv = tmp_path / "domains.tsv"
        tsv.write_text(
            "protein\tdomain\tstart\tend\n"
            "protA\tPkinase\t10\t250\n"
            "protA\tSH2\t300\t380\n"
            "protB\tWD40\t5\t200\n",
            encoding="utf-8",
        )
        out = tmp_path / "domain.png"

        from jsrc.plot.domain import cmd

        args = Namespace(tsv=str(tsv), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_domain_missing_columns_raises(self, tmp_path):
        tsv = tmp_path / "bad.tsv"
        tsv.write_text("foo\tbar\n1\t2\n", encoding="utf-8")
        out = tmp_path / "domain.png"

        from jsrc.plot.domain import cmd

        args = Namespace(tsv=str(tsv), o=str(out), dpi=72)
        with pytest.raises(SystemExit, match="TSV must have columns"):
            cmd(args)


class TestPlotCis:
    def test_cis_elements_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        bed = tmp_path / "elements.bed"
        bed.write_text(
            "chr1\t10\t50\tTATA_box\n"
            "chr1\t100\t120\tCAAT_box\n"
            "chr2\t5\t30\tGC_box\n",
            encoding="utf-8",
        )
        out = tmp_path / "cis.png"

        from jsrc.plot.cis import cmd

        args = Namespace(bed=str(bed), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_cis_skips_comments_and_empty_lines(self, tmp_path):
        pytest.importorskip("matplotlib")
        bed = tmp_path / "elements.bed"
        bed.write_text(
            "# track name=custom\n"
            "chr1\t10\t50\tTATA\n"
            "\n"
            "chr1\t100\t120\tCAAT\n",
            encoding="utf-8",
        )
        out = tmp_path / "cis.png"

        from jsrc.plot.cis import cmd

        args = Namespace(bed=str(bed), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_cis_short_bed_line_skipped(self, tmp_path):
        """BED lines with fewer than 4 columns are skipped gracefully."""
        pytest.importorskip("matplotlib")
        bed = tmp_path / "elements.bed"
        bed.write_text(
            "chr1\t10\t50\tTATA\n" "chr1\t100\t120\n",  # too short, should skip
            encoding="utf-8",
        )
        out = tmp_path / "cis.png"

        from jsrc.plot.cis import cmd

        args = Namespace(bed=str(bed), o=str(out), dpi=72)
        cmd(args)
        assert out.exists()


class TestPlotCircosLite:
    def test_circoslite_basic(self, tmp_path):
        pytest.importorskip("matplotlib")
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\nATGCGCGTAA\n>chr2\nGGCCATGC\n", encoding="utf-8")
        out = tmp_path / "circos.png"

        from jsrc.plot.circoslite import cmd

        args = Namespace(fa=str(fa), w=4, o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_circoslite_small_window(self, tmp_path):
        pytest.importorskip("matplotlib")
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\nATGCGCGTAA\n", encoding="utf-8")
        out = tmp_path / "circos.png"

        from jsrc.plot.circoslite import cmd

        args = Namespace(fa=str(fa), w=1, o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_circoslite_no_sequences_raises(self, tmp_path):
        pytest.importorskip("matplotlib")
        fa = tmp_path / "empty.fa"
        fa.write_text("", encoding="utf-8")
        out = tmp_path / "circos.png"

        from jsrc.plot.circoslite import cmd

        args = Namespace(fa=str(fa), w=10, o=str(out), dpi=72)
        with pytest.raises(SystemExit, match="No sequences found"):
            cmd(args)

    def test_circoslite_window_too_small_raises(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\nATGC\n", encoding="utf-8")

        from jsrc.plot.circoslite import cmd

        args = Namespace(fa=str(fa), w=0, o="/dev/null", dpi=72)
        with pytest.raises(SystemExit, match="-w must be >= 1"):
            cmd(args)


class TestPlotDotplot:
    def test_dotplot_identical_sequences(self, tmp_path):
        pytest.importorskip("matplotlib")
        fa1 = tmp_path / "a.fa"
        fa2 = tmp_path / "b.fa"
        fa1.write_text(">a\nATGCATGC\n", encoding="utf-8")
        fa2.write_text(">b\nATGCATGC\n", encoding="utf-8")
        out = tmp_path / "dot.png"

        from jsrc.plot.dotplot import cmd

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_dotplot_different_sequences(self, tmp_path):
        pytest.importorskip("matplotlib")
        fa1 = tmp_path / "a.fa"
        fa2 = tmp_path / "b.fa"
        fa1.write_text(">a\nATGCATGC\n", encoding="utf-8")
        fa2.write_text(">b\nGGGGGGGG\n", encoding="utf-8")
        out = tmp_path / "dot.png"

        from jsrc.plot.dotplot import cmd

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=3, o=str(out), dpi=72)
        cmd(args)
        assert out.exists()

    def test_dotplot_invalid_k_raises(self, tmp_path):
        fa1 = tmp_path / "a.fa"
        fa2 = tmp_path / "b.fa"
        fa1.write_text(">a\nATGC\n", encoding="utf-8")
        fa2.write_text(">b\nATGC\n", encoding="utf-8")

        from jsrc.plot.dotplot import cmd

        args = Namespace(fa1=str(fa1), fa2=str(fa2), k=0, o=str(tmp_path / "x.png"), dpi=72)
        with pytest.raises(SystemExit, match="-k must be >= 1"):
            cmd(args)

    def test_dotplot_sequence_too_short_raises(self, tmp_path):
        fa1 = tmp_path / "a.fa"
        fa2 = tmp_path / "b.fa"
        fa1.write_text(">a\nAT\n", encoding="utf-8")
        fa2.write_text(">b\nATGC\n", encoding="utf-8")

        from jsrc.plot.dotplot import cmd

        args = Namespace(
            fa1=str(fa1), fa2=str(fa2), k=3, o=str(tmp_path / "x.png"), dpi=72
        )
        with pytest.raises(SystemExit, match="Sequence length must be >= k"):
            cmd(args)

    def test_dotplot_empty_fasta_raises(self, tmp_path):
        fa1 = tmp_path / "a.fa"
        fa2 = tmp_path / "b.fa"
        fa1.write_text(">a\nATGC\n", encoding="utf-8")
        fa2.write_text("", encoding="utf-8")

        from jsrc.plot.dotplot import cmd
        from jsrc.plot.dotplot import _first_seq

        with pytest.raises(SystemExit, match="No sequence found"):
            _first_seq(str(fa2))
