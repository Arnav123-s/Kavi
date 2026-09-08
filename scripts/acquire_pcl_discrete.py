"""Acquire the original textbook page; refuse changed source content."""

import hashlib
import subprocess
from scripts.pcl_discrete_source import DATA, URL, DIGEST


def acquire():
    DATA.mkdir(parents=True, exist_ok=True)
    target = DATA/'logic.html'
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != DIGEST:
            raise ValueError('Existing textbook differs; inspect before replacement')
        return
    temporary = DATA/'logic.html.download'
    subprocess.run(['curl.exe','--silent','--show-error','--fail','--location',
                    '--max-time','45','--output',str(temporary),URL],check=True)
    if hashlib.sha256(temporary.read_bytes()).hexdigest() != DIGEST:
        raise ValueError('Textbook fingerprint changed; review the new edition')
    temporary.replace(target)


if __name__ == '__main__':
    acquire()
    print('Original discrete-mathematics teaching source verified.')
