from jsrc.plot.core import get_gene_structure, natural_sort_key


class TestNaturalSortKey:
    def test_pure_text_sorts_alphabetically(self):
        keys = ["chrX", "chrY", "chr1"]
        sorted_keys = sorted(keys, key=natural_sort_key)
        assert sorted_keys == ["chr1", "chrX", "chrY"]

    def test_numeric_portions_sort_as_numbers(self):
        keys = ["chr10", "chr2", "chr1"]
        sorted_keys = sorted(keys, key=natural_sort_key)
        assert sorted_keys == ["chr1", "chr2", "chr10"]

    def test_mixed_text_and_numbers(self):
        keys = ["gene_12_abc", "gene_2_xyz", "gene_1_def"]
        sorted_keys = sorted(keys, key=natural_sort_key)
        assert sorted_keys == ["gene_1_def", "gene_2_xyz", "gene_12_abc"]

    def test_case_insensitive(self):
        keys = ["chrX", "chra", "chrB"]
        sorted_keys = sorted(keys, key=natural_sort_key)
        assert sorted_keys == ["chra", "chrB", "chrX"]


class TestGetGeneStructure:
    def test_basic_cds_features(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "##gff\n"
            "chr1\tsrc\tmRNA\t1\t100\t.\t+\t.\tID=mrna1;Parent=gene1;\n"
            "chr1\tsrc\tCDS\t1\t50\t.\t+\t.\tParent=mrna1\n"
            "chr1\tsrc\tCDS\t60\t100\t.\t+\t.\tParent=mrna1\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(str(gff), ["gene1"], feature_types=["CDS"])
        assert "gene1" in coords
        assert len(coords["gene1"]) == 2
        assert coords["gene1"][0] == (1, 50)
        assert coords["gene1"][1] == (60, 100)

    def test_direct_cds_parent_no_mrna(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tCDS\t10\t30\t.\t+\t.\tParent=gene1;\n"
            "chr1\tsrc\tCDS\t40\t60\t.\t+\t.\tParent=gene1;\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(str(gff), ["gene1"], feature_types=["CDS"])
        assert "gene1" in coords
        assert len(coords["gene1"]) == 2

    def test_exon_features(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\texon\t5\t15\t.\t+\t.\tParent=gene1;\n"
            "chr1\tsrc\texon\t25\t35\t.\t+\t.\tParent=gene1;\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(str(gff), ["gene1"], feature_types=["exon"])
        assert "gene1" in coords
        assert len(coords["gene1"]) == 2

    def test_skip_comments_and_malformed_lines(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "# this is a comment\n"
            "chr1\tsrc\tCDS\t1\t10\t.\t+\t.\tParent=gene1;\n"
            "incomplete line without enough fields\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(str(gff), ["gene1"], feature_types=["CDS"])
        assert len(coords["gene1"]) == 1

    def test_unknown_gene_id_returns_empty_list(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tCDS\t1\t10\t.\t+\t.\tParent=gene1;\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(
            str(gff), ["gene_nonexistent"], feature_types=["CDS"]
        )
        assert coords["gene_nonexistent"] == []

    def test_non_target_feature_skipped(self, tmp_path):
        gff = tmp_path / "test.gff"
        gff.write_text(
            "chr1\tsrc\tCDS\t1\t10\t.\t+\t.\tParent=gene1;\n"
            "chr1\tsrc\tUTR\t11\t20\t.\t+\t.\tParent=gene1;\n",
            encoding="utf-8",
        )
        coords = get_gene_structure(str(gff), ["gene1"], feature_types=["CDS"])
        assert len(coords["gene1"]) == 1
