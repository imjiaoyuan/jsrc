from jsrc.common.gff import parse_gff_attributes


def test_parse_gff_attributes_eq_and_gtf_style():
    attrs1 = parse_gff_attributes('ID=gene1;Parent=tx1;Name="Gene 1";')
    assert attrs1["ID"] == "gene1"
    assert attrs1["Parent"] == "tx1"
    assert attrs1["Name"] == "Gene 1"

    attrs2 = parse_gff_attributes('gene_id "g1"; transcript_id "t1";')
    assert attrs2["gene_id"] == "g1"
    assert attrs2["transcript_id"] == "t1"

