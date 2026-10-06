#!/usr/bin/env python3
"""Fetch the exact CC-BY 4.0 author archive; do not execute downloaded code."""
import argparse
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

URL = "https://zenodo.org/api/records/7894213/files/Inverse_Photobleach_Flow-main.zip/content"
SHA256 = "2c35036167001afae6e04906453e3640eb5eee275cfa742d67dbffe3a3b251bf"
FILES = ["README.md", "seg_funcs.py", "control_example.ipynb", "protrusion_example.ipynb",
         "data/control_example.tif", "data/protrusion_example.tif"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "Inverse_Photobleach_Flow")
    args = parser.parse_args()
    archive = urlopen(URL, timeout=60).read()
    assert hashlib.sha256(archive).hexdigest() == SHA256, "Archive hash changed; stop and inspect."
    with ZipFile(io.BytesIO(archive)) as zipped:
        for name in FILES:
            matches = [n for n in zipped.namelist() if n.endswith("/" + name)]
            assert len(matches) == 1, (name, matches)
            destination = args.output / name
            destination.parent.mkdir(exist_ok=True, parents=True)
            contents = zipped.read(matches[0])
            if destination.exists():
                assert destination.read_bytes() == contents, f"Existing file differs; refusing overwrite: {destination}"
            else:
                destination.write_bytes(contents)
    print(f"Verified archive and extracted {len(FILES)} allowlisted files to {args.output}.")


if __name__ == "__main__":
    main()
