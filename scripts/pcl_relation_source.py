"""Projection of original basic dependency annotations; no generated sentences."""

import hashlib
from pathlib import Path

REVISION = '4dc8e10cf32352e11ab2c46e024b19853b91546e'
DATA = Path(__file__).resolve().parents[1]/'private/ewt-source-20260908'
EXPECTED = {
    'en_ewt-ud-train.conllu': 'a049fc40822e21593ff89ccd0a4b081443f09fae71b61f813c624aa598f6c566',
    'en_ewt-ud-dev.conllu': '14a82ce2c4c4648c3e7c4efc76872c85c5f4c39643fcb7f9c91a45a58157a270',
    'en_ewt-ud-test.conllu': '0612e45914359e4b36d187ef2bfeaf66fc8933210925be985c5fbf6a9e311036',
    'README.md': 'fc0c5d1344f56442af1501c8c2c850c002924ab6fe20f7de6f8667c1ebc46a79',
    'LICENSE.txt': 'b3d1b0f4c6ae151f7eb78738f46ebd5ee140f8a7f76501ba26af123140d35ae7',
}


def records(path):
    for block in path.read_text(encoding='utf-8').strip().split('\n\n'):
        metadata, tokens = {}, []
        for line in block.splitlines():
            if line.startswith('# ') and ' = ' in line:
                key, value = line[2:].split(' = ', 1)
                metadata[key] = value
            elif line and not line.startswith('#'):
                fields = line.split('\t')
                if len(fields) != 10:
                    raise ValueError('Invalid CoNLL-U row')
                if fields[0].isdigit():
                    tokens.append(fields)
        if not 4 <= len(tokens) <= 18:
            continue
        roots = [t for t in tokens if t[6] == '0' and t[3] == 'VERB']
        if len(roots) != 1:
            continue
        root = roots[0][0]
        for token in tokens:
            if token[6] != root or token[7] not in ('nsubj', 'obj'):
                continue
            events = tuple('candidate' if t[0] == token[0] else
                           'predicate' if t[0] == root else 'other' for t in tokens)
            sentence = metadata['sent_id']
            yield {'id': sentence+':'+token[0], 'sentence': sentence,
                   'document': sentence.rsplit('-', 1)[0], 'events': events,
                   'label': int(token[7] == 'obj')}


def packet(per_class=24):
    for name, digest in EXPECTED.items():
        if hashlib.sha256((DATA/name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Source fingerprint mismatch: {name}')
    banks, seen_patterns, seen_documents = {}, set(), set()
    for name, source, quota in [('training', 'train', per_class),
                                ('development', 'dev', 12), ('final', 'test', 24)]:
        rows = sorted(records(DATA/f'en_ewt-ud-{source}.conllu'),
                      key=lambda row: hashlib.sha256(row['id'].encode()).hexdigest())
        selected, counts, patterns = [], [0, 0], set()
        for row in rows:
            if (counts[row['label']] == quota or row['events'] in seen_patterns
                    or row['events'] in patterns or row['document'] in seen_documents):
                continue
            selected.append(row)
            patterns.add(row['events'])
            counts[row['label']] += 1
        if counts != [quota, quota]:
            raise ValueError(f'Insufficient source cases for {name}: {counts}')
        banks[name] = selected
        seen_patterns.update(patterns)
        seen_documents.update(row['document'] for row in selected)
    counts = [0, 0]
    banks['first'] = []
    for row in banks['training']:
        if counts[row['label']] < per_class//2:
            banks['first'].append(row)
            counts[row['label']] += 1
    return banks


def fingerprints():
    return {path.name: {'bytes': path.stat().st_size,
                       'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(DATA.iterdir()) if path.is_file()}
