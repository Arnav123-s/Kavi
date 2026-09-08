"""Render completed discrete-logic results from public aggregate evidence."""

import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    record = json.loads((root/'experiments/2026-09-08-pcl-discrete.json').read_text())
    names = list(record['arms'])
    labels = [f'{"Coupled" if "couplings-6" in n else "Uncoupled"} / seed {n.rsplit("-",1)[1]}' for n in names]
    correct = [record['arms'][n]['final']['correct'] for n in names]
    wrong = [record['arms'][n]['final']['wrong'] for n in names]
    unresolved = [record['arms'][n]['final']['unresolved'] for n in names]
    plt.rcParams.update({'svg.hashsalt':'pcl-discrete-20260908','svg.fonttype':'none',
                         'font.family':'DejaVu Sans','font.size':11})
    fig, ax = plt.subplots(figsize=(10,5.6))
    ax.barh(labels,correct,color='#267c72',label='Correct')
    ax.barh(labels,wrong,left=correct,color='#c96b53',label='Wrong')
    ax.barh(labels,unresolved,left=[a+b for a,b in zip(correct,wrong)],color='#d9dee7',label='Unresolved')
    ax.axvline(record['controls']['constant_true_correct'],color='#555555',linestyle='--')
    ax.invert_yaxis()
    ax.set_xlim(0,32)
    ax.set_xticks(range(0,33,4))
    ax.set_xlabel('Final textbook cases (five untrained compound structures)')
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Discrete logic: reuse of learned truth functions',fontsize=17,y=.97)
    fig.text(.25,.89,'Dashed line: always true, 22/32. Untrained circuit: 0/32.',fontsize=10)
    fig.legend(loc='lower center',ncol=3,bbox_to_anchor=(.57,.09),frameon=False)
    fig.text(.04,.03,'Arnav123-s | Original textbook tables. Truth functions learned; syntax and composition supplied.',fontsize=9)
    fig.subplots_adjust(left=.25,right=.95,top=.83,bottom=.28)
    path=root/'experiments/pcl-discrete-20260908.svg'
    fig.savefig(path,metadata={'Creator':'Arnav123-s','Date':None})
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    fig.savefig(root/'private/pcl-discrete-preview.png',dpi=130)
    plt.close(fig)


if __name__ == '__main__':
    main()
