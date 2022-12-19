import shutil
import zipfile
from pathlib import Path

import requests
from tqdm.auto import tqdm


def download_bach_dataset(path: Path, force=False) -> None:
    """
    Downloads the Bach midi dataset into a given directory. The directory
    is created if it does not exist.

    Parameters
    ----------
    path
        Directory where the dataset should be saved
    force
        Whether to remove `path` contents if already present
    """

    assert not path.exists() or path.is_dir(
    ), "Given path has to be a directory or should not exist"

    bach_filename = "bach.zip"
    bach_url = f"https://www.bachcentral.com/{bach_filename}"
    zip_path = path.joinpath(bach_filename)

    path.mkdir(parents=True, exist_ok=True)

    if zip_path.exists() and not force:
        # dataset was already downloaded
        return

    # download the dataset with a progress bar
    with requests.get(bach_url, stream=True) as r:
        content_length = int(r.headers.get("Content-Length"))

        with tqdm.wrapattr(r.raw, 'read', total=content_length, desc='Downloading Bach dataset') as raw:
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(raw, f)

    # unzip
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(path)

    # remove junk
    shutil.rmtree(path.joinpath('__MACOSX'))
    path.joinpath('bach/.DS_Store').unlink()


if __name__ == '__main__':
    print(download_bach_dataset(Path('out'), force=True))
