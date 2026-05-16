import json

from jsrc.grn.anno2json import annotation_to_json
from jsrc.grn.net2json import network_to_json


class TestNetworkToJson:
    def test_basic_conversion(self, tmp_path):
        tsv = tmp_path / "net.tsv"
        tsv.write_text("A\tB\t0.5\nB\tC\t1.2\n", encoding="utf-8")
        out = tmp_path / "grn.json"

        links, node_count = network_to_json(str(tsv), str(out))
        assert node_count == 3
        assert len(links) == 2

        data = json.loads(out.read_text())
        assert data[0]["source"] == "A"
        assert data[0]["target"] == "B"
        assert data[0]["val"] == 0.5
        assert data[1]["source"] == "B"
        assert data[1]["target"] == "C"
        assert data[1]["val"] == 1.2

    def test_preserves_underscores(self, tmp_path):
        tsv = tmp_path / "net.tsv"
        tsv.write_text("gene_A\tgene_B\t1.0\n", encoding="utf-8")
        out = tmp_path / "grn.json"

        links, _ = network_to_json(str(tsv), str(out))
        assert links[0]["source"] == "gene_A"
        assert links[0]["target"] == "gene_B"

    def test_invalid_weight_skips_row(self, tmp_path, capsys):
        tsv = tmp_path / "net.tsv"
        tsv.write_text("A\tB\tnot_a_number\nC\tD\t1.0\n", encoding="utf-8")
        out = tmp_path / "grn.json"

        links, node_count = network_to_json(str(tsv), str(out))
        assert len(links) == 1
        assert node_count == 2

    def test_short_row_skipped(self, tmp_path):
        tsv = tmp_path / "net.tsv"
        tsv.write_text("A\tB\t1.0\nC\tD\n", encoding="utf-8")
        out = tmp_path / "grn.json"

        links, _ = network_to_json(str(tsv), str(out))
        assert len(links) == 1

    def test_empty_file(self, tmp_path, capsys):
        tsv = tmp_path / "empty.tsv"
        tsv.write_text("", encoding="utf-8")
        out = tmp_path / "grn.json"

        links, node_count = network_to_json(str(tsv), str(out))
        assert len(links) == 0
        assert node_count == 0


class TestAnnotationToJson:
    def test_basic_annotation(self, tmp_path):
        tsv = tmp_path / "anno.tsv"
        tsv.write_text(
            "AT5G01010\tAnthranilate synthase\tAT5G01010\n", encoding="utf-8"
        )
        out = tmp_path / "annotation.json"

        anno = annotation_to_json(str(tsv), str(out))
        assert "AT5G01010" in anno
        assert anno["AT5G01010"]["p"] == "AT5G01010"
        assert anno["AT5G01010"]["d"] == "Anthranilate synthase"

        data = json.loads(out.read_text())
        assert data == anno

    def test_preserves_underscores_in_id(self, tmp_path):
        tsv = tmp_path / "anno.tsv"
        tsv.write_text("gene_A\t\t", encoding="utf-8")
        out = tmp_path / "annotation.json"

        anno = annotation_to_json(str(tsv), str(out))
        assert "gene_A" in anno

    def test_incomplete_row_returns_empty_strings(self, tmp_path):
        tsv = tmp_path / "anno.tsv"
        tsv.write_text("just_id\n", encoding="utf-8")
        out = tmp_path / "annotation.json"

        anno = annotation_to_json(str(tsv), str(out))

        assert anno["just_id"]["p"] == ""
        assert anno["just_id"]["d"] == ""

    def test_empty_line_skipped(self, tmp_path):
        tsv = tmp_path / "anno.tsv"
        tsv.write_text("A\tB\tC\n\nD\tE\tF\n", encoding="utf-8")
        out = tmp_path / "annotation.json"

        anno = annotation_to_json(str(tsv), str(out))
        assert len(anno) == 2
        assert "A" in anno
        assert "D" in anno

    def test_third_column_used_as_mapping_id(self, tmp_path):
        tsv = tmp_path / "anno.tsv"
        tsv.write_text("G1\tDesc\tAT1G01010\n", encoding="utf-8")
        out = tmp_path / "annotation.json"

        anno = annotation_to_json(str(tsv), str(out))
        assert anno["G1"]["p"] == "AT1G01010"
        assert anno["G1"]["d"] == "Desc"
