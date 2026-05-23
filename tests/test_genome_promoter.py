from argparse import Namespace

import pytest
from Bio import SeqIO


class TestPromoterCmd:
    def test_promoter_extraction_plus_strand(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 100 + "ATGCCC" + "T" * 100 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t101\t106\t.\t+\t.\tID=gene1\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="ID",
            feature="gene",
            up=20,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        cmd(args)

        assert out.exists()
        records = list(SeqIO.parse(out, "fasta"))
        assert len(records) == 1
        assert records[0].id == "gene1"
        assert len(records[0].seq) <= 25

    def test_promoter_extraction_minus_strand(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 100 + "ATGCCC" + "T" * 100 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t101\t106\t.\t-\t.\tID=gene2\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("gene2\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="ID",
            feature="gene",
            up=20,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        cmd(args)

        assert out.exists()
        records = list(SeqIO.parse(out, "fasta"))
        assert len(records) == 1
        assert records[0].id == "gene2"

    def test_promoter_no_matching_genes(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 200 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t101\t106\t.\t+\t.\tID=gene1\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("gene999\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="ID",
            feature="gene",
            up=20,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        cmd(args)

        assert out.exists()
        records = list(SeqIO.parse(out, "fasta"))
        assert len(records) == 0

    def test_promoter_boundary_handling(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "ATGCCC" + "T" * 100 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t1\t6\t.\t+\t.\tID=gene1\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="ID",
            feature="gene",
            up=100,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        cmd(args)

        assert out.exists()
        records = list(SeqIO.parse(out, "fasta"))
        assert len(records) == 1

    def test_promoter_negative_values_raise(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\nATGC\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t1\t4\t.\t+\t.\tID=gene1\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("gene1\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="ID",
            feature="gene",
            up=-10,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        with pytest.raises(SystemExit):
            cmd(args)

    def test_promoter_custom_id_field(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 100 + "ATGCCC" + "T" * 100 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t101\t106\t.\t+\t.\tName=mygene\n")

        ids = tmp_path / "ids.txt"
        ids.write_text("mygene\n")

        out = tmp_path / "promoters.fa"

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            ids=str(ids),
            o=str(out),
            id="Name",
            feature="gene",
            up=20,
            down=5,
        )

        from jsrc.genome.promoter import cmd

        cmd(args)

        assert out.exists()
        records = list(SeqIO.parse(out, "fasta"))
        assert len(records) == 1
        assert records[0].id == "mygene"
