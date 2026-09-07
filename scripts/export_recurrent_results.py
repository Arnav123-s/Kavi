"""Export compact evidence and a diagram from the recorded September trial."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    def read(name):
        return json.loads((ROOT / 'runs' / name / 'results.json').read_text(encoding='utf-8'))

    initial = read('recurrent-configuration-20260907-r2')
    repaired = read('recurrent-configuration-20260907-coverage')
    startup = read('recurrent-configuration-20260907')
    summary = {'author': 'Arnav123-s', 'date': '2026-09-07', 'base_commit': 'f504600',
               'protocol': '../docs/RECURRENT_CONFIGURATION_PROTOCOL.md',
               'startup_failure': {key: startup[key] for key in ('state', 'error', 'seconds')},
               'conditions': []}
    for name, record, folder_name in (
            ('initial', initial, 'recurrent-configuration-20260907-r2'),
            ('coverage-repair', repaired, 'recurrent-configuration-20260907-coverage')):
        condition = {key: record.get(key) for key in ('state', 'seeds', 'seconds', 'ui_pacing_seconds',
                      'worker_cpu_seconds', 'limits', 'resources', 'work', 'criteria', 'unavailable',
                      'external_bytes_before_final_results')}
        condition['name'] = name
        condition['final_external_folder_bytes'] = sum(p.stat().st_size for p in
            (ROOT / 'runs' / folder_name).rglob('*') if p.is_file())
        condition['trials'] = []
        for trial in record['trials']:
            view = {key: trial[key] for key in ('seed', 'fits', 'old_obligations', 'new_labeled_sequences',
                    'model_bytes', 'state_counts', 'frozen_hashes', 'frozen_unchanged', 'exact', 'before_feedback')}
            view['development_accuracy_before_repairs'] = [r['before_feedback']['correct'] for r in trial['repair_rounds']]
            view['development_accuracy_after'] = trial['development_after']['correct']
            view['repair_labels'] = sum(len(r['teaching']) for r in trial['repair_rounds'])
            view['final'] = {stage: {key: values[key] for key in ('correct', 'total', 'unresolved')}
                             | {'first_failures': values['failures'][:3]}
                             for stage, values in trial['final'].items()}
            condition['trials'].append(view)
        summary['conditions'].append(condition)

    # Recheck that no stream in the new final banks was in the earlier final banks.
    overlaps = {}
    for bank in ('parity', 'late'):
        def rows(folder):
            path = ROOT / 'runs' / folder / f'final-{bank}-bank.json'
            return {tuple(s) for s in json.loads(path.read_text(encoding='utf-8'))}
        overlaps[bank] = len(rows('recurrent-configuration-20260907-r2') &
                            rows('recurrent-configuration-20260907-coverage'))
    summary['old_new_final_bank_overlap'] = overlaps
    summary['sampling_note'] = 'Each condition uses one 256-case bank per task, repeated across three merge-order seeds; counts across seeds are model-input evaluations.'

    destinations = (
        ('recurrent-configuration-20260907-coverage', '7-frozen-successor.json', 'recurrent-20260907-model.json'),
        ('recurrent-configuration-20260907-coverage', '7-frozen-foundation.json', 'recurrent-20260907-foundation.json'),
        ('recurrent-configuration-20260907-r2', '7-frozen-successor.json', 'recurrent-20260907-initial-model.json'))
    summary['artifacts'] = {}
    for folder, filename, destination in destinations:
        raw = (ROOT / 'runs' / folder / filename).read_bytes()
        (ROOT / 'experiments' / destination).write_bytes(raw)
        summary['artifacts'][destination] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    (ROOT / 'experiments/2026-09-07-recurrent-configuration.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Vector figure: observed scores and exact learned transition table.
    model = json.loads((ROOT / 'experiments/recurrent-20260907-model.json').read_bytes())
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="750" viewBox="0 0 1200 750">',
           '<title>Recurrent configuration: measured results and learned connections</title>',
           '<desc>Initial and repaired accuracy for three seeds, and the eight-state learned transition table.</desc>',
           '<rect width="1200" height="750" fill="#f5f7fb"/>',
           '<style>text{font-family:Arial,sans-serif;fill:#17304b}.small{font-size:16px}.body{font-size:19px}.head{font-size:24px;font-weight:bold}</style>',
           '<text x="40" y="48" font-size="30" font-weight="bold">Learning recurrent configurations</text>',
           '<text x="40" y="80" class="body">Measured 7 September 2026 · Arnav123-s</text>',
           '<rect x="28" y="104" width="555" height="580" rx="12" fill="white"/>',
           '<rect x="602" y="104" width="570" height="580" rx="12" fill="white"/>',
           '<text x="50" y="144" class="head">Longer streams: correct out of 256</text>',
           '<text x="624" y="144" class="head">The learned connections</text>',
           '<text x="50" y="177" class="small">Blue: initial course   Green: coverage repair</text>']
    for index, seed in enumerate((7, 19, 43)):
        y = 230 + 100 * index
        values = [initial['trials'][index]['final']['successor']['correct'],
                  repaired['trials'][index]['final']['successor']['correct']]
        svg.append(f'<text x="50" y="{y-10}" class="body">Seed {seed}</text>')
        for offset, score, color in zip((0, 29), values, ('#527ea8', '#24765e')):
            svg.append(f'<rect x="140" y="{y+offset-23}" width="{score/256*330:.2f}" height="23" fill="{color}" rx="3"/>')
            svg.append(f'<text x="{150+score/256*330:.2f}" y="{y+offset-5}" class="small">{score}</text>')
    svg.extend(['<text x="50" y="535" class="body">Final graph: 8 states · 32 transitions</text>',
                '<text x="50" y="568" class="body">195 bytes for the serialized model</text>',
                '<text x="50" y="609" class="small">Runtime and learning storage are additional.</text>',
                '<text x="50" y="638" class="small">Both conditions retain the old domain exactly.</text>'])
    headers = ['State', '?a', '?b', 'a', 'b', 'Output']
    for col, header in enumerate(headers):
        svg.append(f'<text x="{628+col*85}" y="195" class="body" font-weight="bold">{header}</text>')
    for state, row in enumerate(model['transitions']):
        y = 232 + 43 * state
        svg.append(f'<rect x="619" y="{y-27}" width="532" height="40" fill="{"#eaf0f7" if state%2==0 else "#ffffff"}"/>')
        for col, value in enumerate([state] + row + [model['outputs'][state]]):
            svg.append(f'<text x="{638+col*85}" y="{y}" class="body">{value}</text>')
    svg.extend(['<text x="624" y="608" class="small">Every token follows one connection.</text>',
                '<text x="624" y="636" class="small">State identifiers are learned, without concept names.</text>',
                '<text x="40" y="715" class="small">Conditions use different final banks. Each bank is repeated across seeds; exact audits cover every finite stream.</text>',
                '</svg>'])
    (ROOT / 'experiments/recurrent-20260907-results.svg').write_text('\n'.join(svg), encoding='utf-8')
    print(json.dumps({'artifacts': summary['artifacts'], 'final_bank_overlap': overlaps,
                      'conditions': [{k: v for k, v in c.items() if k in ('name', 'seconds', 'final_external_folder_bytes')}
                                     for c in summary['conditions']]}))


if __name__ == '__main__':
    main()
