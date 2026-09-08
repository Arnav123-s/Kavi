"""A restricted physical upper bound, with explicit supplied proof premises."""

import hashlib
import json
from pathlib import Path

from .composable_configurations import Configuration, encoded, fit


def teach_radius_bound(registry, work):
    # All three annotations belong to Crowell and Shotwell 7-m5. This is a
    # correction to an already scored question, not a held-out examination.
    lessons=[('height_difference',2,[((35.,23.),12.)],('science_difference','science_sum','science_ratio')),
             ('normal_complement',1,[((2/3,),1/3)],('one','science_difference','half','double')),
             ('radius_scale',2,[((12.,1/3),72.)],('science_ratio','double','science_work'))]
    result=[]
    for name,arity,examples,operations in lessons:
        graph=fit(registry,name,examples,operations,work,arity=arity)
        if graph is None:
            raise ValueError('Published bound correction did not fit')
        registry.install(name,graph)
        result.append({'name':name,'source':'Crowell and Shotwell 7-m5','examples':examples,'operations':operations,'graph':graph.record()})
    registry.install('radius_bound',Configuration(3,(
        ('height_difference',(0,1)),('normal_complement',(2,)),('radius_scale',(3,4))),5))
    return result


def record(registry):
    names=('height_difference','normal_complement','radius_scale','radius_bound')
    dependencies={n:hashlib.sha256(encoded(c.record())).hexdigest() for n,c in registry.definitions.items() if n not in names}
    return {'format':'kavi-guarded-radius-bound-1','substrate':registry.substrate,'dependencies':dependencies,
            'definitions':{n:registry.definitions[n].record() for n in names}}


def install(registry,path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data['substrate']!=registry.substrate:
        raise ValueError('Radius bound substrate changed')
    for name,digest in data['dependencies'].items():
        if name not in registry.definitions or hashlib.sha256(encoded(registry.definitions[name].record())).hexdigest()!=digest:
            raise ValueError('Radius bound dependency changed')
    for name,definition in data['definitions'].items():
        registry.install(name,Configuration.decode(definition))


def answer(registry,descent,rise,normal_fraction,work,*,positive_friction,starts_at_rest,crest):
    if positive_friction is not True or starts_at_rest is not True or crest is not True:
        raise ValueError('This bound requires a start from rest, positive frictional loss and a circular crest')
    if not 0<=normal_fraction<1 or not descent>rise>=0:
        raise ValueError('This bound requires descent > rise >= 0 and 0 <= normal fraction < 1')
    upper=registry.execute('radius_bound',(descent,rise,normal_fraction),work)
    return {'relation':'<','quantity':'radius','upper':upper,'unit':'m',
        'explanation':'Positive frictional loss gives v² < 2g(descent − rise). At the crest, N=fmg and mg−N=mv²/r give v²=(1−f)gr. Since g>0 and 1−f>0, dividing preserves the inequality: r < 2(descent−rise)/(1−f).',
        'status':'learned numerical configuration with supplied physical interpretation and proof rule'}
