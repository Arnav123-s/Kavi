"""Acquire the human-written GSM8K base files, excluding generated variants."""

import hashlib
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / 'private/human-math-20260907'
    folder.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    records = []
    base = 'https://raw.githubusercontent.com/openai/grade-school-math/master/'
    for name in ('grade_school_math/data/train.jsonl', 'grade_school_math/data/test.jsonl', 'LICENSE'):
        if time.monotonic() - started > 60:
            raise TimeoutError('Acquisition budget exhausted')
        url = base + name
        with urlopen(Request(url, headers={'User-Agent':'Kavi research/1.0'}), timeout=20) as response:
            raw = response.read(12_000_001)
        if len(raw) > 12_000_000:
            raise ValueError('Source file exceeds its size ceiling')
        target = folder / Path(name).name
        target.write_bytes(raw)
        records.append({'file':target.name, 'url':url, 'bytes':len(raw),
                        'sha256':hashlib.sha256(raw).hexdigest()})
    record = {'title':'GSM8K base corpus', 'authors':'Cobbe et al.',
              'paper':'https://arxiv.org/abs/2110.14168',
              'source':'https://github.com/openai/grade-school-math',
              'construction':'Human problem writers; base train/test only. Socratic and model-generated files excluded.',
              'retrieved':'2026-09-07', 'files':records}
    (folder / 'source.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
