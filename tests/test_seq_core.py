from pathlib import Path

import pytest

from jsrc.core import ResourceNotFoundError, check_input, parse_gff_attributes


def test_parse_gff_attributes_eq_and_gtf_style():
    attrs1 = parse_gff_attributes('ID=gene1;Parent=tx1;Name="Gene 1";')
    assert attrs1["ID"] == "gene1"
    assert attrs1["Parent"] == "tx1"
    assert attrs1["Name"] == "Gene 1"

    attrs2 = parse_gff_attributes('gene_id "g1"; transcript_id "t1";')
    assert attrs2["gene_id"] == "g1"
    assert attrs2["transcript_id"] == "t1"


def test_parse_gff_attributes_unescapes_gff3_percent_encoding():
    # GFF3 spec URL-encodes reserved chars in attribute values.
    attrs = parse_gff_attributes("ID=gene1;Note=hello%3Bworld;Desc=a%2Cb%3Dc")
    assert attrs["ID"] == "gene1"
    assert attrs["Note"] == "hello;world"
    assert attrs["Desc"] == "a,b=c"


def test_check_input_returns_path_when_exists(tmp_path):
    f = tmp_path / "x.fa"
    f.write_text("data", encoding="utf-8")
    assert check_input(f) == Path(f)


def test_check_input_raises_resource_not_found(tmp_path):
    missing = tmp_path / "nope.fa"
    with pytest.raises(ResourceNotFoundError):
        check_input(missing)


def test_check_input_label_in_message(tmp_path):
    missing = tmp_path / "nope.fa"
    with pytest.raises(ResourceNotFoundError, match="FASTA"):
        check_input(missing, label="FASTA file")
