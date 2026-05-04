import sys

import numpy as np
import pytest

from jsrc import cli


def _run_cli(monkeypatch, argv):
    monkeypatch.setattr(sys, "argv", argv)
    cli.main()


@pytest.mark.parametrize("module_name", ["job", "vision", "plot", "gs", "grn"])
def test_module_parent_help_via_cli(module_name, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["jsrc", module_name])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1
    out = capsys.readouterr().out
    assert f"usage: jsrc {module_name}" in out


def test_cli_debug_mode_raises_original_exception(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "jsrc",
            "--debug",
            "seq",
            "window",
            "-fa",
            "/tmp/does-not-exist.fa",
            "-w",
            "10",
            "-s",
            "2",
        ],
    )
    with pytest.raises(FileNotFoundError):
        cli.main()


def test_job_submit_and_list_flow(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "xdg"))
    monkeypatch.setenv("JSRC_JOBS_FILE", str(tmp_path / "jobs.tsv"))

    _run_cli(monkeypatch, ["jsrc", "job", "submit", "echo job-test", "-N", "test-job"])
    submit_out = capsys.readouterr().out
    assert "job_id\t" in submit_out
    assert "status\trunning" in submit_out

    _run_cli(monkeypatch, ["jsrc", "job", "ls", "-f", "tsv", "-l", "1"])
    list_out = capsys.readouterr().out
    assert list_out.startswith("job_id\tstatus\tpid")
    assert "echo job-test" in list_out


def test_gs_split_flow(tmp_path, monkeypatch):
    data_dir = tmp_path / "gs"
    data_dir.mkdir(parents=True)
    np.save(data_dir / "y.npy", np.array([1.0, 2.0, 3.0, 4.0]))
    (data_dir / "sample_ids.txt").write_text(
        "real_1\nreal_2\nsim_1\nreal_3\n", encoding="utf-8"
    )

    _run_cli(
        monkeypatch,
        ["jsrc", "gs", "split", "-i", str(data_dir), "--folds", "2", "--seed", "1"],
    )
    assert (data_dir / "cv_indices" / "fold_0_train.txt").exists()
    assert (data_dir / "cv_indices" / "fold_0_test.txt").exists()


def test_grn_centrality_flow(tmp_path, capsys, monkeypatch):
    edge_file = tmp_path / "net.tsv"
    edge_file.write_text("A\tB\t1\nB\tC\t2\n", encoding="utf-8")

    _run_cli(
        monkeypatch, ["jsrc", "grn", "centrality", "-i", str(edge_file), "--top", "2"]
    )
    out = capsys.readouterr().out
    assert "nodes\t3" in out
    assert "node\tin_degree\tout_degree\ttotal_degree" in out


def test_plot_dotplot_flow(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    fa1 = tmp_path / "a.fa"
    fa2 = tmp_path / "b.fa"
    fa1.write_text(">a\nATGCATGC\n", encoding="utf-8")
    fa2.write_text(">b\nATGCATGC\n", encoding="utf-8")
    out_png = tmp_path / "dot.png"

    _run_cli(
        monkeypatch,
        [
            "jsrc",
            "plot",
            "dotplot",
            "-fa1",
            str(fa1),
            "-fa2",
            str(fa2),
            "-k",
            "3",
            "-o",
            str(out_png),
        ],
    )
    assert out_png.exists()
    assert out_png.stat().st_size > 0


def test_vision_traits_flow(tmp_path, capsys, monkeypatch):
    cv2 = pytest.importorskip("cv2")
    img = np.zeros((120, 120, 3), dtype=np.uint8)
    cv2.rectangle(img, (20, 20), (100, 100), (255, 255, 255), -1)
    image_path = tmp_path / "leaf.png"
    cv2.imwrite(str(image_path), img)

    _run_cli(monkeypatch, ["jsrc", "vision", "traits", "-i", str(image_path)])
    out = capsys.readouterr().out
    assert "area\t" in out
    assert "solidity\t" in out
