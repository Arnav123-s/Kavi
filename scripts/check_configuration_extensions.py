"""Read-only checks for the composition, science and alignment reports."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

from kavi.composable_configurations import Work
from kavi.finite_state_audit import compare
from kavi.inequality_pathway import answer as bound_answer, install
from kavi.published_learning import load_science
from kavi.recurrent_configuration import Configuration
from scripts.run_published_lessons import first_exam, final_exam
from scripts.run_scientific_curriculum import evaluate, practice


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    'README.md', 'docs/DESIGN.md', 'docs/DOCUMENTATION_INDEX.md',
    'docs/PROJECT_ASSESSMENT.md', 'docs/DESIGN_ALIGNMENT_AUDIT.md',
    'docs/REUSABLE_RELATIONAL_CONFIGURATIONS.md',
    'docs/CONFIGURATION_LAB_PROTOCOL.md', 'docs/SCIENTIFIC_CURRICULUM_PROTOCOL.md',
    'docs/PUBLISHED_LESSONS_PROTOCOL.md', 'docs/PUBLISHED_BOUND_CORRECTION.md',
    'docs/CONVERSATION.md', 'docs/ENGLISH_CONFIGURATION_PROTOCOL.md',
    'docs/EQUATIONS_AS_PATHWAY_COMPONENTS.md', 'docs/INPUT_DRIVEN_PATHWAYS.md',
    'docs/PHYSICAL_PATHWAY_RESEARCH.md',
    'docs/INTERACTING_CONFIGURATIONS.md', 'docs/ENGLISH_DATA_ATTRIBUTION.md',
    'docs/INCREMENTAL_ENGLISH_PROTOCOL.md', 'docs/LEARNED_INQUIRY_PROTOCOL.md',
    'docs/PATHWAY_TRANSFER_PROTOCOL.md', 'docs/DIRECT_EVENT_LEARNING_PROTOCOL.md',
    'docs/ADAPTIVE_EVENT_PROTOCOL.md', 'docs/PRIMARY_NOTEBOOK_CURRICULUM.md',
    'experiments/2026-09-07-composable-science-and-conversation.md',
    'experiments/2026-09-07-published-english.md',
    'experiments/2026-09-07-incremental-inquiry-transfer.md', 'experiments/README.md',
)


def verify_artifact(record):
    body = (ROOT / 'experiments' / record['file']).read_bytes()
    assert len(body) == record['bytes'], record['file']
    assert hashlib.sha256(body).hexdigest() == record['sha256'], record['file']


def verify_implementation(hashes, revision=None):
    checked = 0
    for path, digest in hashes.items():
        if not path.endswith(('.py', '.md')):
            continue
        if revision is None:
            source = (ROOT / path).read_text(encoding='utf-8').encode('utf-8')
        else:
            source = subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)
            source = source.replace(b'\r\n', b'\n')
        assert hashlib.sha256(source).hexdigest() == digest, (revision, path)
        checked += 1
    return checked


def verify_english():
    previous = json.loads((ROOT / 'experiments/2026-09-07-published-english.json').read_text(encoding='utf-8'))
    checks = 0
    artifacts = 0
    for label in ('initial', 'expanded'):
        course = previous[label]
        verify_artifact(course['artifact'])
        artifacts += 1
        checks += verify_implementation(course['source_hashes'], previous[label+'_implementation_revision'])
    assert previous['retention']['retained_correct'] == 68
    assert len(previous['retention']['regressions']) == 32
    assert len(previous['retention']['improvements']) == 19

    sharing = json.loads((ROOT / 'experiments/2026-09-07-english-sharing.json').read_text(encoding='utf-8'))
    verify_artifact({'file':'english-20260907-shared-model.json',
                     'bytes':sharing['shared_bytes'], 'sha256':sharing['shared_sha256']})
    checks += verify_implementation(sharing['source_hashes'])
    artifacts += 1

    courses = json.loads((ROOT / 'experiments/2026-09-07-incremental-inquiry-transfer.json').read_text(encoding='utf-8'))['courses']
    for course in courses.values():
        assert course['state'] == 'completed'
        verify_artifact(course['artifact'])
        artifacts += 1
        checks += verify_implementation(course['source_hashes'])
    assert courses['incremental']['followup']['correct'] == 94
    assert courses['transfer']['followup']['correct'] == 98
    assert courses['events']['followup']['correct'] == 11
    adaptive = courses['adaptive']
    assert adaptive['online_before_correct'] == 8
    assert adaptive['online_after_correct'] == 24
    assert adaptive['final_training']['correct'] == adaptive['final_training']['total'] == 168
    assert adaptive['followup_direct']['correct'] == 15
    assert adaptive['initial_adaptive_control']['correct'] == 31
    assert adaptive['followup_adaptive']['correct'] == 29
    assert adaptive['followup_adaptive']['unresolved'] == 0
    assert len(adaptive['corrections']) == 24
    assert sum(r.get('replayed_source_lessons', 0) for r in adaptive['corrections']) == 918
    assert sum(r.get('added_connections', 0) for r in adaptive['corrections'] if r['action'] == 'extension') == 27
    assert not any(r['regressions'] for r in adaptive['corrections'])
    parts = adaptive['partitions']
    taught = set(parts['initial_training']) | set(parts['new_teaching'])
    assert not taught & (set(parts['development']) | set(parts['followup']))
    assert not set(parts['development']) & set(parts['followup'])
    assessments = adaptive['followup_adaptive']['self_assessment']
    assert assessments == {'needs_help':{'total':63, 'correct':19}, 'can_propose':{'total':39, 'correct':10}}
    assert adaptive['frozen_artifact_unchanged']

    # A scope distinction that pairwise operation names alone cannot encode.
    from fractions import Fraction
    x, y, z = map(Fraction, (12, 6, 2))
    assert x/(y/z) == 4 and (x/y)/z == 1
    catalogue = json.loads((ROOT/'curriculum/primary-notebooks-20260907.json').read_text(encoding='utf-8'))
    assert catalogue['author'] == 'Arnav123-s' and catalogue['teaching_runs'] == 0
    assert len(catalogue['records']) == len({row['id'] for row in catalogue['records']}) == 10
    for source in catalogue['records']:
        assert source['training_status'] == 'not_trained'
        assert not source['full_text_acquired'] and source['file_sha256'] is None
        assert all(url.startswith('https://') for url in source['urls'])
        if source['diagnosis_evidence'] is not None:
            assert source['diagnosis_evidence']['inferred_from_writing'] is False
    return {'artifacts':artifacts, 'implementation_hashes':checks, 'completed_courses':len(courses),
            'source_catalogue_records':len(catalogue['records']), 'source_teaching_runs':0}


def main():
    record = json.loads((ROOT / 'experiments/2026-09-07-composable-science-and-conversation.json')
                        .read_text(encoding='utf-8'))
    implementation_hashes = {}
    for name in ('composition', 'science', 'published_lessons', 'bound_correction'):
        run = record[name]
        assert run['state'] == 'completed'
        artifact = run['artifact']
        body = (ROOT / 'experiments' / artifact['file']).read_bytes()
        assert len(body) == artifact['bytes']
        assert hashlib.sha256(body).hexdigest() == artifact['sha256']
        for path, digest in run['source_hashes'].items():
            if path.endswith('.py'):
                implementation_hashes[path] = digest
                source = (ROOT / path).read_text(encoding='utf-8').encode('utf-8')
                assert hashlib.sha256(source).hexdigest() == digest, path

    arithmetic = ROOT / 'experiments/library-20260907-compiled.json'
    initial = load_science(ROOT / 'experiments/science-20260907-initial-model.json', arithmetic)
    first = evaluate(initial, first_exam(), Work())
    assert (first['correct'], first['total']) == (0, 8)
    model = load_science(ROOT / 'experiments/science-20260907-published-model.json',
                         arithmetic, extended=True)
    final = evaluate(model, final_exam(), Work())
    assert (final['correct'], final['total']) == (4, 5)
    assert evaluate(model, first_exam(), Work())['correct'] == 8
    assert evaluate(model, practice(), Work())['correct'] == 13
    install(model.registry, ROOT / 'experiments/science-20260907-radius-bound.json')
    corrected = bound_answer(model.registry, 35., 23., 2/3, Work(),
                             positive_friction=True, starts_at_rest=True, crest=True)
    assert abs(corrected['upper'] - 72.) < 1e-10
    assert evaluate(model, final_exam()[:4] + practice(), Work())['correct'] == 17
    assert record['bound_correction']['new_unseen_inequality_questions'] == 0
    assert record['science']['lesson_presentations'] == 192
    assert record['published_lessons']['lesson_presentations'] == 16
    assert sum(t['work']['candidate_proposals']
               for t in record['published_lessons']['teaching']) == 11725
    assert record['science']['after_sharing']['bytes_before'] == \
        record['science']['after_sharing']['bytes_after'] == 4205

    old = Configuration.decode((ROOT / 'experiments/recurrent-20260907-foundation.json').read_bytes())
    new = Configuration.decode((ROOT / 'experiments/recurrent-20260907-model.json').read_bytes())
    preserved = compare(old, new, old.alphabet)
    assert len(old.outputs) == 2 and len(new.outputs) == 8 and preserved['equivalent']
    english = verify_english()

    link_count = diagram_count = 0
    for document in DOCUMENTS:
        path = ROOT / document
        text = path.read_text(encoding='utf-8')
        assert 'Author: [Arnav123-s](https://github.com/Arnav123-s)' in text, document
        assert text.count('$$') % 2 == 0, document
        fence = None
        for line in text.splitlines():
            match = re.match(r'^(\x60{3,}|~{3,})(.*)$', line)
            if match:
                marker, info = match.groups()
                if fence is None:
                    fence = marker
                    if info == 'mermaid':
                        diagram_count += 1
                elif marker[0] == fence[0] and len(marker) >= len(fence):
                    fence = None
        assert fence is None, document
        for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', text):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            assert (path.parent / unquote(target.split('#')[0])).exists(), (document, target)
            link_count += 1
    print(json.dumps({'artifact_hashes': 4, 'implementation_hashes': len(implementation_hashes),
                      'documents': len(DOCUMENTS), 'local_links': link_count,
                      'diagram_fences': diagram_count,
                      'initial_exam': '0/8', 'frozen_fresh_exam': '4/5',
                      'corrected_bound': corrected['upper'], 'old_retention': '17/17',
                      'whole_graph_old_behavior_preserved': preserved['equivalent'],
                      'english_and_adaptive_checks':english,
                      'new_training': False}, indent=2))


if __name__ == '__main__':
    main()
