import json
import logging
from argparse import Namespace
from unittest.mock import patch

import pytest

from jsrc.seq.fetch import _parse_ids, cmd


class TestFetchParseIds:
    def test_literal_ids(self):
        result = _parse_ids(["NM_001", "NR_002"])
        assert result == ["NM_001", "NR_002"]

    def test_ids_from_file(self, tmp_path):
        f = tmp_path / "ids.txt"
        f.write_text("NM_001\nNR_002\n\n", encoding="utf-8")
        result = _parse_ids([str(f)])
        assert result == ["NM_001", "NR_002"]

    def test_mixed_ids_and_file(self, tmp_path):
        f = tmp_path / "ids.txt"
        f.write_text("NR_002\n", encoding="utf-8")
        result = _parse_ids(["NM_001", str(f), "NR_003"])
        assert result == ["NM_001", "NR_002", "NR_003"]


class TestFetchCmd:
    def test_no_ids_raises(self):
        args = Namespace(
            ids=[],
            email="test@example.com",
            o=None,
            format="fasta",
            db="nucleotide",
            json=False,
        )
        with pytest.raises(SystemExit):
            cmd(args)

    @patch("jsrc.seq.fetch.Entrez.efetch")
    @patch("jsrc.seq.fetch.SeqIO.parse")
    def test_fetch_fasta_stdout(self, mock_parse, mock_efetch, capsys, caplog):
        caplog.set_level(logging.INFO)

        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        mock_parse.return_value = [
            SeqRecord(Seq("ATGC"), id="NM_001", description="Test sequence")
        ]

        args = Namespace(
            ids=["NM_001"],
            email="test@example.com",
            o=None,
            format="fasta",
            db="nucleotide",
            json=False,
        )
        cmd(args)

        out = capsys.readouterr().out
        assert ">NM_001" in out
        assert "ATGC" in out

    @patch("jsrc.seq.fetch.Entrez.efetch")
    @patch("jsrc.seq.fetch.SeqIO.parse")
    def test_fetch_genbank_json(self, mock_parse, mock_efetch, capsys, caplog):
        caplog.set_level(logging.INFO)

        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        mock_parse.return_value = [
            SeqRecord(
                Seq("ATGC"),
                id="NM_001",
                description="Test desc",
                annotations={"molecule_type": "DNA"},
            )
        ]

        args = Namespace(
            ids=["NM_001"],
            email="test@example.com",
            o=None,
            format="genbank",
            db="nucleotide",
            json=True,
        )
        cmd(args)

        payload = json.loads(capsys.readouterr().out)
        assert len(payload) == 1
        assert payload[0]["id"] == "NM_001"
        assert payload[0]["length"] == 4

    @patch("jsrc.seq.fetch.Entrez.efetch")
    @patch("jsrc.seq.fetch.SeqIO.parse")
    def test_fetch_to_file(self, mock_parse, mock_efetch, tmp_path, caplog):
        caplog.set_level(logging.INFO)

        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord

        mock_parse.return_value = [
            SeqRecord(Seq("ATGC"), id="NM_001", description="Test")
        ]

        out_file = tmp_path / "result.fa"
        args = Namespace(
            ids=["NM_001"],
            email="test@example.com",
            o=str(out_file),
            format="fasta",
            db="nucleotide",
            json=False,
        )
        cmd(args)

        assert "Wrote 1 record(s) to" in caplog.text
        content = out_file.read_text()
        assert ">NM_001" in content

    @patch("jsrc.seq.fetch.Entrez.efetch")
    def test_fetch_failure(self, mock_efetch, capsys):
        mock_efetch.side_effect = Exception("Network error")

        args = Namespace(
            ids=["NM_001"],
            email="test@example.com",
            o=None,
            format="fasta",
            db="nucleotide",
            json=False,
        )
        with pytest.raises(SystemExit) as e:
            cmd(args)
        assert "Network error" in str(e.value)

    @patch("jsrc.seq.fetch.Entrez.efetch")
    @patch("jsrc.seq.fetch.SeqIO.parse")
    def test_fetch_empty_result(self, mock_parse, mock_efetch):
        mock_parse.return_value = []

        args = Namespace(
            ids=["NM_001"],
            email="test@example.com",
            o=None,
            format="fasta",
            db="nucleotide",
            json=False,
        )
        with pytest.raises(SystemExit) as e:
            cmd(args)
        assert "No records returned" in str(e.value)
