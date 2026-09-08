"""Render the public aggregate results without reading original sentences."""

import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'experiments/2026-09-08-pcl-relations.json').read_text())
    names = list(data['arms'])
    labels = [f'{"Coupled" if "couplings-4" in name else "Uncoupled"} / seed {name.rsplit("-",1)[1]}' for name in names]
    correct = [data['arms'][name]['final']['correct'] for name in names]
    wrong = [data['arms'][name]['final']['wrong'] for name in names]
    unresolved = [data['arms'][name]['final']['unresolved'] for name in names]
    plt.rcParams.update({'svg.hashsalt': 'pcl-relations-20260908', 'svg.fonttype': 'none',
                         'font.family': 'DejaVu Sans', 'font.size': 11})
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.barh(labels, correct, color='#267c72', label='Correct')
    ax.barh(labels, wrong, left=correct, color='#c96b53', label='Wrong')
    ax.barh(labels, unresolved, left=[a+b for a,b in zip(correct,wrong)],
            color='#d9dee7', label='Unresolved')
    ax.axvline(data['controls']['constant_subject'], color='#555555', linestyle='--')
    ax.axvline(data['controls']['supplied_position_rule'], color='#415b99', linestyle=':')
    ax.set_xlim(0,48)
    ax.set_xticks(range(0,49,8))
    ax.set_xlabel('Final questions (48 unfamiliar position patterns)')
    ax.invert_yaxis()
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Ordered relations: teaching success, weak generalization', fontsize=16, x=.52, y=.97)
    fig.text(.25,.89,'Dashed: constant subject 24/48. Dotted: supplied position rule 46/48.',fontsize=10)
    fig.legend(loc='lower center', ncol=3, bbox_to_anchor=(.57,.09), frameon=False)
    fig.text(.04,.03,'Arnav123-s | Original EWT annotations; selected word and verb positions supplied. No raw-language claim.', fontsize=9)
    fig.subplots_adjust(left=.25,right=.96,top=.83,bottom=.28)
    svg = root/'experiments/pcl-relations-20260908.svg'
    fig.savefig(svg, metadata={'Creator':'Arnav123-s','Date':None})
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(root/'private/pcl-relations-preview.png',dpi=130)
    plt.close(fig)


if __name__ == '__main__':
    main()
