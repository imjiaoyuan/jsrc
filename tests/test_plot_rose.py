from argparse import Namespace
from unittest import mock

from jsrc.plot.rose import cmd


def test_rose_copies_html_and_opens_browser(tmp_path):
    sources = tmp_path / "sources"
    sources.mkdir(exist_ok=True)
    (sources / "rose.html").write_text("<html></html>")

    with (
        mock.patch("webbrowser.open") as mock_open,
        mock.patch("tempfile.mkdtemp", return_value=str(tmp_path)),
        mock.patch(
            "importlib.resources.files",
            return_value=sources,
        ),
        mock.patch(
            "importlib.resources.as_file",
            side_effect=lambda d: mock.MagicMock(
                __enter__=lambda _: sources, __exit__=lambda *_: None
            ),
        ),
    ):
        args = Namespace()
        cmd(args)

        mock_open.assert_called_once()
