"""Acquire an unchanged UCI edition of the original Iris measurements."""

import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'private/iris-source-20260908'
URL = 'https://archive.ics.uci.edu/static/public/53/iris.zip'


def acquire(archive_path=None):
    DATA.mkdir(parents=True, exist_ok=True)
    raw = Path(archive_path).read_bytes() if archive_path else urlopen(URL, timeout=30).read()
    (DATA/'iris.zip').write_bytes(raw)
    manifest = {'source': URL, 'author': 'R. A. Fisher', 'edition': 'UCI bezdekIris.data',
                'license': 'CC BY 4.0', 'doi': '10.24432/C56C76', 'synthetic': False,
                'archive_sha256': hashlib.sha256(raw).hexdigest(), 'archive_bytes': len(raw), 'files': []}
    archive = zipfile.ZipFile(io.BytesIO(raw))
    for name in ('bezdekIris.data', 'iris.data', 'iris.names'):
        body = archive.read(name)
        (DATA/name).write_bytes(body)
        manifest['files'].append({'name': name, 'bytes': len(body), 'sha256': hashlib.sha256(body).hexdigest()})
    (DATA/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, help='Archive already acquired from the stated UCI URL')
    acquire(parser.parse_args().archive)
