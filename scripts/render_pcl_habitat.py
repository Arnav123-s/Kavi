"""Architecture illustration for the learned boundary experiment."""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def main():
    root=Path(__file__).resolve().parents[1]
    plt.rcParams.update({'svg.hashsalt':'pcl-habitat-20260908','svg.fonttype':'none',
                         'font.family':'DejaVu Sans','font.size':11})
    fig,ax=plt.subplots(figsize=(11,7));ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    def box(x,y,w,h,text,color='#edf4fa',size=11):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',
                     facecolor=color,edgecolor='#506f89',linewidth=1.4))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size)
    ax.text(.5,.96,'Kavi: a learned template around a learned circuit',ha='center',fontsize=19)
    ax.text(.5,.90,'First implementation: structural input roles, not a complete semantic world',ha='center',fontsize=11)
    box(.045,.20,.91,.62,'',color='#eff7f5')
    ax.text(.5,.775,'LEARNED HABITAT / TEMPLATE',ha='center',fontsize=14,fontweight='bold')
    box(.085,.51,.34,.18,'First 8 lessons\n2 inferred roles · 1 arrangement\nvalue — binary connective — value')
    box(.575,.51,.34,.18,'10 additional lessons\n3 inferred roles · 2 arrangements\nAdds unary connective — value')
    ax.annotate('',xy=(.56,.60),xytext=(.44,.60),arrowprops={'arrowstyle':'->','lw':2,'color':'#267c72'})
    ax.text(.5,.66,'Rebuild',ha='center',fontsize=10)
    box(.18,.29,.64,.13,'LEARNED INNER CIRCUIT\nImpulses + interactions + output rules\nSuccessor must preserve earlier supported answers',color='white')
    ax.annotate('',xy=(.5,.43),xytext=(.5,.51),arrowprops={'arrowstyle':'->','lw':1.5})
    ax.text(.5,.235,'Admit template and circuit together; keep the old world on rejection',ha='center',fontsize=10)
    box(.045,.065,.91,.085,'FIXED DEVICE / SEARCH ENVELOPE\nComponent bounds, execution budget and pause/stop controls',color='#f0f0f0',size=10)
    fig.text(.04,.025,'Arnav123-s | 3 runs: 8/8 old answers retained, 18/18 source cases, 32/32 compatibility regression.',fontsize=9)
    fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.045)
    path=root/'experiments/pcl-habitat-20260908.svg'
    fig.savefig(path,metadata={'Creator':'Arnav123-s','Date':None})
    path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    fig.savefig(root/'private/pcl-habitat-preview.png',dpi=130);plt.close(fig)


if __name__=='__main__':main()
