"""Display separate harder-logic and English-interpretation measurements."""

import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    root=Path(__file__).resolve().parents[1]
    r=json.loads((root/'experiments/2026-09-08-pcl-english-logic.json').read_text())
    hard=r['hard']['7']; english=r['arms']['7']['final']
    results=[(hard['tables']['correct'],36),(sum(p['correct'] for p in hard['puzzles'].values()),2),
             (english['same_pattern']['correct'],5),(english['new_pattern']['correct'],3)]
    plt.rcParams.update({'svg.hashsalt':'pcl-english-logic-20260908','svg.fonttype':'none',
                         'font.family':'DejaVu Sans','font.size':11})
    fig,ax=plt.subplots(figsize=(10,5))
    labels=['Additional logic cases','Multi-premise puzzles','English: familiar pattern','English: new wording']
    for i,(correct,total) in enumerate(results):
        ax.barh(i,100,color='#d9dee7')
        ax.barh(i,100*correct/total,color='#267c72')
        ax.text(102,i,f'{correct}/{total}',va='center')
    ax.set_yticks(range(4),labels);ax.invert_yaxis();ax.set_xlim(0,115)
    ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Correct (%) — different denominators shown at right')
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Stronger formal tests; English transfer remains narrow',fontsize=16,y=.97)
    fig.text(.32,.86,'All three seeds have these scores. Gray marks unsolved cases.',fontsize=10)
    fig.text(.035,.04,'Arnav123-s | Logic uses supplied formalization/search. English uses supplied atomic clause spans.',fontsize=9)
    fig.subplots_adjust(left=.32,right=.95,top=.80,bottom=.25)
    path=root/'experiments/pcl-english-logic-20260908.svg'
    fig.savefig(path,metadata={'Creator':'Arnav123-s','Date':None})
    path.write_text('\n'.join(s.rstrip() for s in path.read_text().splitlines())+'\n')
    fig.savefig(root/'private/pcl-english-logic-preview.png',dpi=130);plt.close(fig)


if __name__=='__main__':main()
