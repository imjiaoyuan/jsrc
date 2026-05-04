import json
from argparse import Namespace

from jsrc.seq.window import cmd


def test_seq_window_json_output(tmp_path, capsys):
    fasta = tmp_path / "a.fa"
    fasta.write_text(">s1\nATGCGCGTAA\n", encoding="utf-8")
    args = Namespace(fa=str(fasta), id=None, w=4, s=2, head=3, json=True)
    cmd(args)
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["sequence_id"] == "s1"
    assert payload["window_count"] >= 1
    assert "windows_head" in payload


def test_seq_window_uses_longest_record_by_default(tmp_path, capsys):
    fasta = tmp_path / "mix.fa"
    fasta.write_text(">s1\nATGC\n>s2\nATGCATGCAT\n", encoding="utf-8")
    args = Namespace(fa=str(fasta), id=None, w=4, s=2, head=2, json=True)
    cmd(args)
    payload = json.loads(capsys.readouterr().out)
    assert payload["sequence_id"] == "s2"
    assert payload["sequence_length"] == 10
