"""Extract original examination text and published keys without fabricating fixes."""

import json
import re

import pdfplumber
import pypdfium2 as pdfium

from scripts.acquire_psychology_sources import FOLDER, acquire, digest

EXAMS = {
    'mit-exam2-2009-sol.pdf': 'https://ocw.mit.edu/courses/9-00sc-introduction-to-psychology-fall-2011/fa63e525f4e385855930031652f20dde_MIT9_00SCF11_exam2_2009sol.pdf',
    'mit-exam3-sol.pdf': 'https://ocw.mit.edu/courses/9-00sc-introduction-to-psychology-fall-2011/4782483bc4ca2c61e20678af9036e5a1_MIT9_00SCF11_exam3_sol.pdf',
}


def plain(value):
    return ' '.join(value.split())


def parse_2009(path):
    with pdfplumber.open(path) as pdf:
        keys = {int(number): ord(letter)-65 for number, letter in
                re.findall(r'(\d+)\)\s*([A-D])', pdf.pages[0].extract_text())}
        if set(keys) != set(range(1, 51)):
            raise ValueError('Incomplete 2009 answer sheet')
        body = '\n'.join(page.extract_text() or '' for page in pdf.pages[4:])
    parts = re.split(r'(?m)^\s*(\d{1,2})\)\s*', body)
    rows, excluded, seen = [], [], set()
    for index in range(1, len(parts), 2):
        number, chunk = int(parts[index]), parts[index+1]
        if number in seen or number not in keys:
            break
        seen.add(number)
        key = f'mit:exam2-2009:{number}'
        # The next section is not part of the final multiple-choice option.
        chunk = re.split(r'(?im)^\s*(?:short.answer|part\s+ii|MIT OpenCourseWare|ANSWER\s*:)', chunk)[0]
        choices = re.split(r'(?m)^\s*([a-d])\.\s*', chunk)
        if choices[1::2] != ['a', 'b', 'c', 'd']:
            excluded.append({'id': key, 'reason': 'Original option labels are missing, duplicated or unordered'})
            continue
        rows.append({'id': key, 'source': 'MIT 9.00 Spring 2009, archived in 9.00SC Fall 2011',
            'question': plain(choices[0]), 'options': list(map(plain, choices[2::2])),
            'answer': keys[number], 'key_origin': 'Original page 1 multiple-choice answer sheet'})
    if seen != set(range(1, 51)):
        raise ValueError('The 2009 question numbering did not cover all 50 questions')
    return rows, excluded


def blue(chars):
    return any(tuple(char.get('non_stroking_color') or ()) == (0., 0., 1.) for char in chars)


def parse_2011(path):
    groups, current, option = {}, None, None
    finished = False
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            for line in page.extract_text_lines(return_chars=True):
                text = line['text'].strip()
                if re.search(r'short[-\s]answer', text, re.I):
                    finished = True
                    break
                if not text or re.fullmatch(r'\d+', text) or text.startswith(('Questions from', '9.00 Final', 'MIT OpenCourseWare')):
                    continue
                question = re.match(r'^(\d{1,2})\.\s+(.+)', text)
                choice = re.match(r'^([A-D])\)\s*(.*)', text)
                if question:
                    number = int(question[1])
                    if number in groups:
                        raise ValueError('Duplicated 2011 question number')
                    current = groups[number] = {'question': [question[2]], 'options': [], 'keys': [], 'page': page_number}
                    option = None
                elif current is not None and choice:
                    option = []
                    current['options'].append((choice[1], option))
                    option.append(choice[2])
                    if blue(line['chars']):
                        current['keys'].append(ord(choice[1])-65)
                elif current is not None:
                    (current['question'] if option is None else option).append(text)
            if finished:
                break
    if set(groups) != set(range(1, 46)):
        raise ValueError('The 2011 multiple-choice numbering did not cover all 45 questions')
    rows, excluded = [], []
    for number, group in groups.items():
        key = f'mit:exam3-2011:{number}'
        if number <= 3:
            excluded.append({'id': key, 'reason': 'Displayed during initial source discovery; reserved out of the final bank'})
        elif [label for label, _ in group['options']] != ['A', 'B', 'C', 'D'] or len(group['keys']) != 1:
            excluded.append({'id': key, 'reason': 'Requires four ordered options and exactly one blue key'})
        else:
            rows.append({'id': key, 'source': 'MIT 9.00SC Fall 2011, Exam 3', 'page': group['page'],
                'question': plain(' '.join(group['question'])),
                'options': [plain(' '.join(lines)) for _, lines in group['options']],
                'answer': group['keys'][0], 'key_origin': 'Original blue answer marking'})
    return rows, excluded


def main():
    sources = [acquire((name, url)) for name, url in EXAMS.items()]
    rows, excluded = [], []
    for name, parser in (('mit-exam2-2009-sol.pdf', parse_2009), ('mit-exam3-sol.pdf', parse_2011)):
        accepted, rejected = parser(FOLDER/name)
        rows.extend(accepted)
        excluded.extend(rejected)
        document = pdfium.PdfDocument(FOLDER/name)
        indices = (0, 4, len(document)-5) if '2009' in name else (0, 4, len(document)-2)
        for index in indices:
            document[index].render(scale=1.25).to_pil().save(FOLDER/(name+f'-page-{index+1}.png'))
    record = {'sources': sources, 'rows': rows, 'excluded': excluded,
              'not_admitted': [{'file': 'mit-exam2-sol.pdf',
                  'reason': 'Embedded glyph layout damages extracted words; no corrected text invented'}]}
    raw = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True).encode('utf-8')
    (FOLDER/'exams.json').write_bytes(raw)
    print(json.dumps({'questions': len(rows), 'excluded': excluded, 'sha256': digest(raw)}))


if __name__ == '__main__':
    main()
