"""Acquire the author's pinned English-to-logic teaching source."""

import hashlib
import subprocess
from scripts.pcl_discrete_source import DATA
from scripts.pcl_english_logic_source import DIGEST
from scripts.acquire_pcl_discrete import acquire as acquire_logic


def acquire():
    acquire_logic()
    target=DATA/'statements.html'
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()!=DIGEST:
            raise ValueError('Existing English source changed; inspect before replacement')
        return
    temporary=DATA/'statements.html.download'
    subprocess.run(['curl.exe','--silent','--show-error','--fail','--location','--max-time','45',
                    '--output',str(temporary),'https://discrete.openmathbooks.org/dmoi3/sec_intro-statements.html'],check=True)
    if hashlib.sha256(temporary.read_bytes()).hexdigest()!=DIGEST:
        raise ValueError('English source fingerprint changed; review the edition')
    temporary.replace(target)


if __name__=='__main__':
    acquire()
    print('Original logic and English source fingerprints verified.')
