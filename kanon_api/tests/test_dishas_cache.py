import importlib
import pathlib
import shutil
import sys
from unittest import mock

cache_dir = pathlib.Path("dishas_cache")


def test_dishas_cache():
    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    if "kanon_api.core.ephemerides.tables" in sys.modules:
        import kanon_api.core.ephemerides.tables

        importlib.reload(kanon_api.core.ephemerides.tables)

    import kanon_api.core.ephemerides.tables

    assert cache_dir.exists()

    files = list(cache_dir.glob("*"))

    assert len(files) > 0

    with open(files[0]) as f:
        mock_open: mock.MagicMock = mock.mock_open(read_data=f.read())

    with mock.patch("builtins.open", mock_open):
        importlib.reload(kanon_api.core.ephemerides.tables)

    assert mock_open.call_count == len(files)
