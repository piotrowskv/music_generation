import shutil
from pathlib import Path

import pytest

from .bach import download_bach_dataset


def test_fails_if_path_is_file(tmpdir):
    path = Path(tmpdir).joinpath('file.txt')
    path.touch()

    with pytest.raises(AssertionError):
        download_bach_dataset(path)


def test_creates_missing_directories(tmpdir):
    path = Path(tmpdir).joinpath('dir1/dir2/dir3')

    assert not path.exists()

    download_bach_dataset(path)

    assert path.exists()


def test_downloads_dataset(tmpdir):
    path = Path(tmpdir)

    download_bach_dataset(path)

    assert path.joinpath('bach.zip').exists()
    assert path.joinpath('bach').is_dir()


def test_does_nothing_if_zip_is_already_present(tmpdir):
    path = Path(tmpdir)

    download_bach_dataset(path)

    shutil.rmtree(path.joinpath('bach'))

    download_bach_dataset(path)

    assert not path.joinpath('bach').exists()


def test_redownloads_when_force(tmpdir):
    path = Path(tmpdir)

    download_bach_dataset(path)

    shutil.rmtree(path.joinpath('bach'))

    download_bach_dataset(path, force=True)

    assert path.joinpath('bach').exists()


def test_removes_junk(tmpdir):
    path = Path(tmpdir)

    download_bach_dataset(path)

    assert not path.joinpath('__MACOSX').exists()
    assert not path.joinpath('bach/.DS_Store').exists()
