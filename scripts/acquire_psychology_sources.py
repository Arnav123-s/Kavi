"""Acquire original psychology lessons and keys into ignored local storage."""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'private/psychology-sources-20260907'
REVISION = 'de7e40c91813dabdc2875df9d0709fc4f46080bb'
RAW = f'https://raw.githubusercontent.com/openstax/osbooks-psychology/{REVISION}/'
MIT = 'https://ocw.mit.edu/courses/9-00sc-introduction-to-psychology-fall-2011/'
CHAPTERS = {2, 6, 7, 8, 11, 15}


class Plain(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(body):
    reader = Plain()
    reader.feed(body)
    return ' '.join(' '.join(reader.parts).split())


def xml_text(element):
    return '' if element is None else ' '.join(''.join(element.itertext()).split())


def digest(body):
    return hashlib.sha256(body).hexdigest()


def acquire(item):
    name, url = item
    path = FOLDER / name
    if not path.exists():
        request = urllib.request.Request(url, headers={'User-Agent': 'Kavi source verification'})
        with urllib.request.urlopen(request, timeout=40) as response:
            body = response.read(8_000_001)
        if len(body) > 8_000_000:
            raise ValueError('Source exceeds the acquisition size bound')
        path.write_bytes(body)
    body = path.read_bytes()
    return {'file': name, 'url': url, 'bytes': len(body), 'sha256': digest(body)}


def openstax_questions(body, module, chapter):
    root = ET.fromstring(body)
    records, rejected = [], []
    for section in root.findall('.//{*}section'):
        if section.get('class') != 'review-questions':
            continue
        for ex in section.findall('./{*}exercise'):
            key = f'openstax:{module}:{ex.get("id")}'
            problem, solution = ex.find('./{*}problem'), ex.find('./{*}solution')
            if problem is None:
                rejected.append({'id': key, 'reason': 'No problem element'})
                continue
            options = problem.findall('./{*}list/{*}item')
            paras = problem.findall('./{*}para')
            answer = xml_text(solution).strip().upper().rstrip('.')
            if len(options) != 4 or answer not in ('A', 'B', 'C', 'D') or not paras:
                rejected.append({'id': key, 'reason': 'Requires four original options and a single original key'})
                continue
            # Exclude image-dependent material rather than silently losing its input.
            if problem.find('.//{*}media') is not None or problem.find('.//{*}figure') is not None:
                rejected.append({'id': key, 'reason': 'Image-dependent problem'})
                continue
            records.append({'id': key, 'source': 'OpenStax Psychology 2e',
                'chapter': chapter, 'module': module, 'section': xml_text(root.find('./{*}title')),
                'question': ' '.join(map(xml_text, paras)), 'options': list(map(xml_text, options)),
                'answer': ord(answer)-ord('A'), 'key_origin': 'Original CNXML solution element'})
    return records, rejected


def mit_questions(body, page):
    records, rejected = [], []
    # The publisher embeds the key as a correct/wrong icon beside each option.
    blocks = re.split(r'<div class="multiple-choice-question"\s+id=', body)[1:]
    for block in blocks:
        identifier = re.match(r'[^>]+', block)[0].strip('"\' ')
        key = f'mit:{page}:{identifier}'
        title = block.split('<fieldset', 1)[0].split('>', 1)[1]
        field = block.split('<fieldset', 1)[-1].split('</fieldset>', 1)[0]
        labels = re.findall(r'<label\b[^>]*>(.*?)</label>', field, re.S)
        answers = [i for i, label in enumerate(labels) if 'correctness-icon-correct' in label]
        if len(labels) != 4 or len(answers) != 1:
            rejected.append({'id': key, 'reason': 'Requires four options and one original correct marker'})
            continue
        options = [plain(re.sub(r'<span\b[^>]*>.*?</span>', '', label, flags=re.S)) for label in labels]
        records.append({'id': key, 'source': 'MIT 9.00SC Fall 2011', 'page': page,
            'question': plain(title), 'options': options, 'answer': answers[0],
            'key_origin': 'Original correctness-icon-correct HTML marker'})
    return records, rejected


def main():
    FOLDER.mkdir(parents=True, exist_ok=True)
    sources = [acquire(('collection.xml', RAW+'collections/psychology-2e.collection.xml')),
               acquire(('openstax-license.txt', RAW+'LICENSE')),
               acquire(('mit-course.html', MIT)),
               acquire(('mit-terms.html', 'https://ocw.mit.edu/pages/privacy-and-terms-of-use/'))]
    collection = ET.fromstring((FOLDER/'collection.xml').read_bytes())
    license_element = collection.find('.//{*}license')
    if 'by-nc-sa/4.0' not in license_element.get('url', ''):
        raise ValueError('Review the changed OpenStax licence before acquisition')
    chapters = collection.findall('./{*}content/{*}subcollection')
    selected = []
    for chapter, section in enumerate(chapters, 1):
        if chapter in CHAPTERS:
            selected.extend((module.get('document'), chapter) for module in section.findall('.//{*}module'))
    with ThreadPoolExecutor(max_workers=4) as pool:
        acquired = list(pool.map(acquire, [(module+'.cnxml', RAW+f'modules/{module}/index.cnxml')
                                           for module, _ in selected]))
    sources.extend(acquired)
    questions, excluded = [], []
    for module, chapter in selected:
        accepted, rejected = openstax_questions((FOLDER/(module+'.cnxml')).read_bytes(), module, chapter)
        questions.extend(accepted)
        excluded.extend(rejected)
    course = (FOLDER/'mit-course.html').read_text(encoding='utf-8')
    linked = set(re.findall(r'href="(/courses/9-00sc-introduction-to-psychology-fall-2011/pages/[^"#?]+)"', course))
    wanted = ('science', 'learning', 'conditioning', 'intelligence', 'thinking', 'memory',
              'personality', 'disorder', 'emotion', 'development', 'social', 'introduction')
    pages = sorted(path for path in linked if any(word in path.rsplit('/', 2)[-2] for word in wanted)
                   and path.count('/') == 5)
    with ThreadPoolExecutor(max_workers=4) as pool:
        acquired = list(pool.map(acquire, [('mit-'+path.rsplit('/', 2)[-2]+'.html', 'https://ocw.mit.edu'+path)
                                           for path in pages]))
    sources.extend(acquired)
    independent = []
    for source in acquired:
        name = source['file'][4:-5]
        accepted, rejected = mit_questions((FOLDER/source['file']).read_text(encoding='utf-8'), name)
        independent.extend(accepted)
        excluded.extend(rejected)
    for name in ('psychopathy', 'intelligence'):
        sources.append(acquire(('noba-'+name+'.html', 'https://nobaproject.com/modules/'+name)))
    records = {'openstax': questions, 'mit': independent, 'excluded': excluded}
    raw = json.dumps(records, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
    (FOLDER/'questions.json').write_bytes(raw)
    manifest = {'author': 'Arnav123-s', 'acquired_utc': datetime.now(timezone.utc).isoformat(),
        'openstax_revision': REVISION, 'sources': sources,
        'openstax_authors': ['Rose M. Spielman', 'William J. Jenkins', 'Marilyn D. Lovett'],
        'openstax_publisher': 'OpenStax, Rice University', 'openstax_edition': 'Psychology 2e, 2020',
        'mit_author': 'John D. E. Gabrieli and MIT OpenCourseWare course contributors',
        'mit_edition': '9.00SC Introduction to Psychology, Fall 2011',
        'noba_authors': {'psychopathy': 'Christopher J. Patrick', 'intelligence': 'Robert Biswas-Diener'},
        'license': 'CC BY-NC-SA 4.0; retain separately marked third-party exclusions',
        'language': 'English', 'gutenberg_used': False, 'fabricated_questions': 0,
        'questions_sha256': digest(raw), 'openstax_questions': len(questions),
        'openstax_chapters': dict(Counter(row['chapter'] for row in questions)),
        'mit_questions': len(independent), 'excluded': excluded,
        'noba_training_status': 'Research source only; no keyed exercises admitted',
        'source_bytes': sum(row['bytes'] for row in sources)}
    (FOLDER/'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: manifest[k] for k in ('openstax_questions', 'openstax_chapters', 'mit_questions',
                                             'questions_sha256', 'source_bytes')}))


if __name__ == '__main__':
    main()
