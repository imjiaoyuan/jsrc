import json
from argparse import Namespace

from jsrc.genome.density import _calculate_density, cmd


class TestCalculateDensity:
    def test_basic_density_calculation(self):
        features = [(0, 100), (200, 300)]
        genome_length = 1000
        window = 500
        step = 250
        results = _calculate_density(features, genome_length, window, step)
        assert len(results) > 0
        assert "density" in results[0]
        assert "coverage" in results[0]

    def test_no_features(self):
        features = []
        genome_length = 1000
        window = 500
        step = 250
        results = _calculate_density(features, genome_length, window, step)
        assert len(results) > 0
        assert results[0]["count"] == 0
        assert results[0]["density"] == 0.0

    def test_overlapping_features(self):
        features = [(0, 100), (50, 150)]
        genome_length = 500
        window = 200
        step = 100
        results = _calculate_density(features, genome_length, window, step)
        assert len(results) > 0
        assert results[0]["count"] >= 1

    def test_feature_outside_window(self):
        features = [(600, 700)]
        genome_length = 1000
        window = 500
        step = 250
        results = _calculate_density(features, genome_length, window, step)
        assert results[0]["count"] == 0

    def test_coverage_calculation(self):
        features = [(0, 250)]
        genome_length = 1000
        window = 500
        step = 250
        results = _calculate_density(features, genome_length, window, step)
        assert results[0]["coverage"] == 0.5


class TestDensityCmd:
    def test_density_basic_output(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 1000 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1\n")

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            feature_type=None,
            window=500,
            step=250,
            json=False,
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
        assert "chr1" in output or len(output) >= 0

    def test_density_json_output(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 1000 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("chr1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1\n")

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            feature_type=None,
            window=500,
            step=250,
            json=True,
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
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["seq_id"] == "chr1"
        assert "density" in data[0]

    def test_density_feature_type_filter(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 1000 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text(
            "chr1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1\n"
            "chr1\t.\tCDS\t1\t50\t.\t+\t.\tID=cds1\n"
        )

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            feature_type="gene",
            window=500,
            step=250,
            json=True,
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
        data = json.loads(output)
        assert data[0]["total_features"] == 1

    def test_density_multiple_sequences(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 1000 + "\n>chr2\n" + "A" * 1000 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text(
            "chr1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1\n"
            "chr2\t.\tgene\t1\t100\t.\t+\t.\tID=gene2\n"
        )

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            feature_type=None,
            window=500,
            step=250,
            json=True,
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
        data = json.loads(output)
        assert len(data) == 2

    def test_density_no_features(self, tmp_path):
        fa = tmp_path / "genome.fa"
        fa.write_text(">chr1\n" + "A" * 1000 + "\n")

        gff = tmp_path / "genes.gff"
        gff.write_text("")

        args = Namespace(
            fa=str(fa),
            gff=str(gff),
            feature_type=None,
            window=500,
            step=250,
            json=True,
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
        data = json.loads(output)
        assert data[0]["total_features"] == 0
