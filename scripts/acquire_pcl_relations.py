"""Acquire pinned original annotations with verified HTTPS and content hashes."""

import hashlib
import subprocess

from scripts.pcl_relation_source import DATA, EXPECTED, REVISION


def acquire():
    DATA.mkdir(parents=True, exist_ok=True)
    for name, digest in EXPECTED.items():
        target = DATA/name
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
                raise ValueError(f'Existing source differs; inspect before replacement: {name}')
            continue
        temporary = DATA/(name+'.download')
        subprocess.run(['curl.exe', '--silent', '--show-error', '--fail', '--location',
                        '--max-time', '60', '--output', str(temporary),
                        f'https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/{REVISION}/{name}'],
                       check=True)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Download fingerprint mismatch: {name}')
        temporary.replace(target)


if __name__ == '__main__':
    acquire()
    print('Original relation source fingerprints verified.')
