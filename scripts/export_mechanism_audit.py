"""Publish compact measurements and a vector diagram from the recorded run."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'runs/mechanism-audit-20260907'


def main():
    result = json.loads((FOLDER / 'results.json').read_text(encoding='utf-8'))
    if result['state'] != 'completed':
        raise ValueError('A completed audit is required')
    causal = result['causal']
    result['causal'] = {'interventions': len(causal['interventions']),
        'behavior_changes': sum(not v['equivalent'] for v in causal['interventions']),
        'state_pair_checks': sum(v['visited_pairs'] for v in causal['interventions']),
        'first_three_witnesses': causal['interventions'][:3],
        'renamings': causal['renamings'], 'unreachable_state': causal['unreachable_state'],
        'commuting_states': causal['commuting_states']}
    for trial in result['alias']['trials']:
        trial['final'].pop('failures')
    for case in result['repair']['cases']:
        for arm in case['arms']:
            failures = arm['final'].pop('failures')
            arm['final']['first_failure'] = failures[0] if failures else None
    result.update(author='Arnav123-s', date='2026-09-07', base_commit='bbe47dca2e2c9fcb947a41c0457416f813fe682b',
        sampling_note='Alias models share one 128-case final bank. Repair models share another. Repeated model-input evaluations are not distinct questions.',
        storage=json.loads((FOLDER / 'storage.json').read_text(encoding='utf-8')))
    result['resources']['gui_observation_after_completion'] = {'working_set_bytes': 43114496,
        'scope': 'Single post-run observation of the separate visible process; not a simultaneous combined peak.'}
    result['implementation_hash_format'] = 'UTF-8 source normalized to LF line endings'
    result['measured_implementation_sha256'] = {name: hashlib.sha256((ROOT / name).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        for name in ('kavi/configuration_composition.py', 'kavi/configuration_repair.py',
                     'kavi/recurrent_configuration.py', 'kavi/finite_state_audit.py',
                     'kavi/procedure_core.py', 'scripts/run_mechanism_audit.py', 'scripts/recurrent_window.py')}
    result['public_artifacts'] = {}
    for source, name in (('alias-7.json', 'alias'), ('arithmetic-bridge.json', 'bridge'),
                         ('composed-catalog.json', 'catalog'), ('repair-19-priority-greedy.json', 'inexact-repair'),
                         ('repair-7-exhaustive.json', 'exact-repair')):
        raw = (FOLDER / source).read_bytes()
        destination = 'mechanism-20260907-' + name + '.json'
        (ROOT / 'experiments' / destination).write_bytes(raw)
        result['public_artifacts'][destination] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    teaching = {tuple(v[0]) for v in json.loads((FOLDER / 'composition-teaching.json').read_text(encoding='utf-8'))}
    promotion = {tuple(v[0]) for v in json.loads((FOLDER / 'composition-promotion.json').read_text(encoding='utf-8'))}
    final = {tuple(v['args']) for v in json.loads((FOLDER / 'composition-final.json').read_text(encoding='utf-8'))}
    result['composition']['input_overlap'] = {'teaching_promotion': len(teaching & promotion),
        'teaching_final': len(teaching & final), 'promotion_final': len(promotion & final)}
    (ROOT / 'experiments/2026-09-07-mechanism-audit.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="890" viewBox="0 0 1240 890">',
        '<title>Configuration reuse and repair: measured results</title>',
        '<desc>A learned shared arithmetic graph, notation sharing, and exact repair results for five search methods.</desc>',
        '<rect width="1240" height="890" fill="#f3f6fa"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#18334c}.small{font-size:17px}.body{font-size:21px}.head{font-size:25px;font-weight:bold}.node{fill:#e7eff8;stroke:#497095;stroke-width:2}</style>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#497095"/></marker></defs>',
        '<text x="40" y="48" font-size="32" font-weight="bold">Learning new configurations from old ones</text>',
        '<text x="40" y="82" class="body">Measured 7 September 2026 · Arnav123-s</text>',
        '<rect x="25" y="105" width="1190" height="310" rx="12" fill="white"/>',
        '<text x="48" y="145" class="head">A new computation learned from four examples</text>',
        '<text x="48" y="179" class="small">338 candidates · 2 consistent arrangements · one selected by the declared tie rule</text>']
    for x, y, w, label in ((60, 225, 110, 'input x'), (60, 305, 110, 'input y'),
                            (275, 265, 150, 'add'), (600, 265, 175, 'multiply'), (950, 265, 185, 'output')):
        svg.extend([f'<rect class="node" x="{x}" y="{y}" width="{w}" height="52" rx="10"/>',
                    f'<text x="{x+w/2}" y="{y+33}" text-anchor="middle" class="body">{label}</text>'])
    for path in ('M170,251 L275,280', 'M170,331 L275,302',
                 'M425,281 C500,228 538,228 600,280', 'M425,302 C500,351 538,351 600,302',
                 'M775,291 L950,291'):
        svg.append(f'<path d="{path}" fill="none" stroke="#497095" stroke-width="2.5" marker-end="url(#arrow)"/>')
    svg.extend(['<text x="463" y="223" class="small">reuse the same sum</text>',
        '<text x="985" y="346" class="body">(x + y)²</text>',
        '<text x="48" y="389" class="body">48/48 promotion cases · 128/128 fresh inputs · 104/104 earlier-operation checks</text>',
        '<rect x="25" y="435" width="510" height="360" rx="12" fill="white"/>',
        '<text x="48" y="478" class="head">Shared notation and skills</text>',
        '<text x="48" y="522" class="body">a and α acquire identical destinations</text>',
        '<text x="48" y="558" class="body">at all 8 states, in all 3 trials.</text>',
        '<text x="48" y="608" class="body">Frozen notation graph: 216 bytes</text>',
        '<text x="48" y="644" class="body">Controller + arithmetic links: 389 bytes</text>',
        '<text x="48" y="680" class="body">New catalog entry: 195 bytes</text>',
        '<text x="48" y="728" class="small">Arithmetic dependency: another 2,272 bytes.</text>',
        '<text x="48" y="761" class="small">Runtime and learning storage are additional.</text>',
        '<rect x="555" y="435" width="660" height="360" rx="12" fill="white"/>',
        '<text x="580" y="478" class="head">Exact repairs across three fault cases</text>'])
    methods = ['uniform greedy', 'priority greedy', 'uniform heated', 'priority heated', 'exhaustive one-edge']
    for i, method in enumerate(methods):
        wins = sum(arm['whole_task']['equivalent'] for case in result['repair']['cases'] for arm in case['arms'] if arm['arm'] == method)
        y = 525 + i * 44
        svg.extend([f'<text x="580" y="{y}" class="body">{method}</text>',
                    f'<rect x="825" y="{y-22}" width="270" height="27" rx="4" fill="#edf1f6"/>',
                    f'<rect x="825" y="{y-22}" width="{90*wins}" height="27" rx="4" fill="#287b63"/>',
                    f'<text x="1120" y="{y}" class="body">{wins}/3</text>'])
    svg.extend(['<text x="580" y="764" class="small">Sample accuracy alone missed one incorrect repair.</text>',
        '<text x="40" y="839" class="small">Heuristic budget: 128 proposals per case. Exhaustive repair: 224. Earlier behavior retained by all arms.</text>',
        '<text x="40" y="869" class="small">Temperature did not improve exact repairs here. These are narrow computational tasks, not an intelligence test.</text>', '</svg>'])
    (ROOT / 'experiments/mechanism-20260907-results.svg').write_text('\n'.join(svg), encoding='utf-8')
    print(json.dumps({'artifacts': result['public_artifacts'], 'overlap': result['composition']['input_overlap']}))


if __name__ == '__main__':
    main()
