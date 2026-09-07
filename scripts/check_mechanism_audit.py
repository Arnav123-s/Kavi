"""Read-only publication checks for the completed configuration audit."""

import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET

from kavi.configuration_composition import ArithmeticBridge, GraphCatalog
from kavi.finite_state_audit import compare
from kavi.procedure_core import ProcedureLibrary
from kavi.recurrent_configuration import Configuration
from scripts.run_mechanism_audit import EXPANDED, reference

ROOT = Path(__file__).resolve().parents[1]


def main():
    record = json.loads((ROOT / 'experiments/2026-09-07-mechanism-audit.json').read_text(encoding='utf-8'))
    assert record['state'] == 'completed' and record['author'] == 'Arnav123-s'
    for name, expected in record['public_artifacts'].items():
        raw = (ROOT / 'experiments' / name).read_bytes()
        assert len(raw) == expected['bytes']
        assert hashlib.sha256(raw).hexdigest() == expected['sha256']
    for name, digest in record['measured_implementation_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_text(encoding='utf-8').encode('utf-8')).hexdigest() == digest
    library = ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json')
    alias = Configuration.decode((ROOT / 'experiments/mechanism-20260907-alias.json').read_bytes())
    assert compare(reference(EXPANDED), alias, EXPANDED)['equivalent']
    assert all(row[alias.alphabet.index('a')] == row[alias.alphabet.index('α')] for row in alias.transitions)
    bridge = ArithmeticBridge.decode((ROOT / 'experiments/mechanism-20260907-bridge.json').read_bytes())
    assert bridge.controller == alias
    assert bridge.answer(['α'] * 111, (1729, 314), library)['value'] == 1729 * 314
    assert bridge.answer(['α'] * 112, (1729, 314), library)['value'] == 1729 + 314
    catalog = GraphCatalog.decode((ROOT / 'experiments/mechanism-20260907-catalog.json').read_bytes())
    assert catalog.execute('relation_01', (12345, 23456), library).value == (12345 + 23456)**2
    assert catalog.execute('add', (12345, 23456), library).value == 12345 + 23456
    assert not any(record['composition']['input_overlap'].values())
    old = Configuration.decode((ROOT / 'experiments/recurrent-20260907-model.json').read_bytes())
    exact = Configuration.decode((ROOT / 'experiments/mechanism-20260907-exact-repair.json').read_bytes())
    inexact = Configuration.decode((ROOT / 'experiments/mechanism-20260907-inexact-repair.json').read_bytes())
    assert compare(old, exact, old.alphabet)['equivalent']
    witness = compare(old, inexact, old.alphabet)['witness']
    assert witness is not None and old.predict(witness) != inexact.predict(witness)
    assert record['causal']['behavior_changes'] == record['causal']['interventions'] == 224
    assert sum(t['learning']['proposed_merges'] for t in record['alias']['trials']) == 461
    assert sum(a['search']['proposals'] for c in record['repair']['cases'] for a in c['arms']) == 1998
    assert len(library.encoded()) + len(bridge.encoded()) + len(catalog.encoded()) == 2856
    for document in ('README.md', 'docs/PROJECT_ASSESSMENT.md', 'docs/MECHANISM_AUDIT_PROTOCOL.md',
                     'experiments/2026-09-07-mechanism-audit.md', 'docs/DESIGN.md',
                     'docs/DOCUMENTATION_INDEX.md', 'docs/PHYSICAL_PATHWAY_RESEARCH.md',
                     'docs/OPEN_ENDED_PATHWAY_LEARNING.md', 'docs/NEURAL_PATHWAY_LEARNING.md',
                     'docs/ANIMAL_LEARNING_AND_CONFIGURATION_CHANGE.md', 'docs/KAVI_ENGINEERING_SPECIFICATION.md',
                     'docs/IMPLEMENTATION_REFERENCE.md', 'docs/GRADUATE_CAPABILITY_PROGRAM.md',
                     'docs/CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md',
                     'docs/STRUCTURAL_SHARING_AND_QUANTUM_RESEARCH.md'):
        path = ROOT / document
        text = path.read_text(encoding='utf-8')
        assert 'Author:' in text and 'Arnav123-s' in text, document
        assert text.count('```') % 2 == 0 and text.count('$$') % 2 == 0, document
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            resolved = path.parent / unquote(target.split('#')[0])
            assert resolved.exists(), (document, target)
    svg = ET.parse(ROOT / 'experiments/mechanism-20260907-results.svg').getroot()
    assert svg.attrib['viewBox'] == '0 0 1240 890'
    assert svg.find('{http://www.w3.org/2000/svg}title') is not None
    print(json.dumps({'artifact_hashes': len(record['public_artifacts']),
        'source_hashes': len(record['measured_implementation_sha256']), 'documents': 15,
        'exact_and_inexact_controls': 'passed', 'data_partition_checks': 'passed',
        'svg_structure': 'passed'}))


if __name__ == '__main__':
    main()
