"""Render measured classification results from the public aggregate record."""

import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def render():
    data = json.loads((ROOT/'experiments/2026-09-08-pcl-classification.json').read_text())
    names, correct, wrong, unresolved = [], [], [], []
    for name, arm in data['arms'].items():
        names.append(name.replace('-', ' · seed '))
        for series, key in ((correct, 'correct'), (wrong, 'wrong'), (unresolved, 'unresolved')):
            series.append(arm['final'][key])
    for name, key in [('Majority class', 'majority'), ('One threshold', 'stump')]:
        names.append(name)
        value = data['controls'][key]['correct']
        correct.append(value); wrong.append(30-value); unresolved.append(0)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none',
                         'svg.hashsalt': 'pcl-classification-20260908'})
    fig, ax = plt.subplots(figsize=(11, 6.3))
    fig.subplots_adjust(left=.2, right=.93, top=.80, bottom=.27)
    y = list(range(len(names)))
    ax.barh(y, correct, color='#24785b', label='Correct')
    ax.barh(y, wrong, left=correct, color='#bd544a', label='Wrong')
    ax.barh(y, unresolved, left=[a+b for a,b in zip(correct,wrong)], color='#d9e1e8', label='Unresolved')
    for index, score in enumerate(correct):
        ax.text(30.4, index, f'{score}/30', va='center', fontsize=10)
    ax.set(yticks=y, yticklabels=names, xlim=(0,32), xticks=[0,5,10,15,20,25,30], xlabel='Held-out original specimens')
    ax.invert_yaxis()
    ax.spines[['top','right','left']].set_visible(False)
    fig.legend(*ax.get_legend_handles_labels(), loc='lower center',
               bbox_to_anchor=(.52,.105), ncols=3, frameon=False)
    fig.text(.04,.94,'PCL: learned phase regions improve a small classification task',fontsize=16,weight='bold')
    fig.text(.04,.88,'All models retain 90/90 teaching answers. Final inputs never update the circuits.',fontsize=11)
    fig.text(.04,.04,'Iris, UCI bezdek edition · 90 teaching / 30 development / 30 final\nNo language or internal-world capability is established. Region winners use zero couplings.',fontsize=10,color='#394858')
    target=ROOT/'experiments/pcl-classification-20260908.svg'
    fig.savefig(target, metadata={'Creator':'Arnav123-s','Date':None})
    target.write_text('\n'.join(line.rstrip() for line in target.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    fig.savefig(ROOT/'private/pcl-classification-preview.png',dpi=140)
    plt.close(fig)


if __name__ == '__main__':
    render()
