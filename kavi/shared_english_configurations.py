"""Share identical acquired substructures without changing their interpretation.

This is a supplied structural transformation, not an unsupervised meaning learner.
Only ordered, exactly matching substructures are shared. No algebraic rewrite or
approximate clustering is used.
"""

from collections.abc import Mapping
import json
import math
from pathlib import Path

from .published_english import RelevanceReasoner,tuples


def share_configuration(source,work,*,share=True):
    if source.get('format')!='kavi-relevant-english-1':
        raise ValueError('Expected an acquired relevant-English configuration')
    nodes,program_nodes=[],[]
    lookup,program_lookup={},{}

    def intern(node,pool,cache):
        work.add('sharing_node_visits')
        key=tuple(node) if node[0]!='ports' else ('ports',tuple(node[1]))
        if share and key in cache:
            work.add('shared_substructures')
            return cache[key]
        index=len(pool)
        pool.append(node)
        cache[key]=index
        return index

    def tree(source_nodes,index,ancestors=()):
        if index in ancestors:
            raise ValueError('Cyclic predicate definition')
        node=source_nodes[index]
        if 'feature' not in node:
            return intern(['ports',list(node['ports'])],nodes,lookup)
        return intern(['branch',node['feature'],
            tree(source_nodes,node['yes'],ancestors+(index,)),
            tree(source_nodes,node['no'],ancestors+(index,))],nodes,lookup)

    def program(node):
        if type(node) is int:
            return intern(['input',node],program_nodes,program_lookup)
        operation,left,right=node
        if operation not in ('+','-','*','/'):
            raise ValueError('Unsupported program operation')
        return intern(['call',operation,program(left),program(right)],program_nodes,program_lookup)

    roots={name:tree(source[name],0) if source[name] else None
           for name in ('relevance','operations','program_router')}
    programs={name:{'arity':entry['arity'],'root':program(entry['program'])}
              for name,entry in sorted(source['programs'].items())}
    return {'format':'kavi-shared-english-1','nodes':nodes,'roots':roots,
            'program_nodes':program_nodes,'programs':programs}


class SharedPredicate:
    def __init__(self,nodes,root,*,operations=False):
        self.nodes,self.root,self.operations=nodes,root,operations

    def activate(self,features,work):
        index,trace=self.root,[]
        while self.nodes[index][0]=='branch':
            _,feature,yes,no=self.nodes[index]
            active=feature in features
            work.add('connection_activations' if self.operations else 'relevance_connections')
            trace.append({'node':index,'condition':feature,'active':active})
            index=yes if active else no
        ports=self.nodes[index][1]
        if self.operations:
            return {op:math.exp(-rank) for rank,op in enumerate(ports)},trace
        return ports,trace


class SharedPrograms(Mapping):
    def __init__(self,nodes,roots):
        self.nodes,self.roots=nodes,roots

    def __len__(self):return len(self.roots)

    def __iter__(self):return iter(self.roots)

    def expand(self,index):
        node=self.nodes[index]
        if node[0]=='input':return node[1]
        return node[1],self.expand(node[2]),self.expand(node[3])

    def __getitem__(self,name):
        entry=self.roots[name]
        return {'arity':entry['arity'],'program':self.expand(entry['root'])}


class SharedEnglishReasoner(RelevanceReasoner):
    def __init__(self,record):
        if record.get('format')!='kavi-shared-english-1':
            raise ValueError('Unknown shared configuration format')
        self.configuration=record
        nodes,roots=record['nodes'],record['roots']
        self._validate(record)
        super().__init__(SharedPredicate(nodes,roots['relevance']),
            SharedPredicate(nodes,roots['operations'],operations=True),
            SharedPredicate(nodes,roots['program_router']) if roots['program_router'] is not None else None,
            SharedPrograms(record['program_nodes'],record['programs']))

    @staticmethod
    def _validate(record):
        for name in ('nodes','program_nodes'):
            for index,node in enumerate(record[name]):
                if node[0] in ('branch','call'):
                    if len(node)!=4 or any(type(r) is not int or not 0<=r<index for r in node[2:]):
                        raise ValueError('Shared connections must point to earlier nodes')
                    if name=='program_nodes' and (node[0]!='call' or node[1] not in ('+','-','*','/')):
                        raise ValueError('Invalid shared arithmetic call')
                    if name=='nodes' and (node[0]!='branch' or not isinstance(node[1],str)):
                        raise ValueError('Invalid predicate branch')
                elif name=='nodes' and node[0]=='ports':
                    if len(node)!=2 or not node[1] or not all(isinstance(v,str) for v in node[1]):
                        raise ValueError('Invalid predicate outputs')
                elif name=='program_nodes' and node[0]=='input':
                    if len(node)!=2 or type(node[1]) is not int or not 0<=node[1]<8:
                        raise ValueError('Invalid argument reference')
                else:raise ValueError('Unknown shared node')
        for name,root in record['roots'].items():
            if root is None and name=='program_router':continue
            if type(root) is not int or not 0<=root<len(record['nodes']):
                raise ValueError('Invalid predicate root')
        for entry in record['programs'].values():
            if type(entry['arity']) is not int or not 2<=entry['arity']<=8:
                raise ValueError('Invalid shared program arity')
            if type(entry['root']) is not int or not 0<=entry['root']<len(record['program_nodes']):
                raise ValueError('Invalid shared program root')

    def record(self):return self.configuration

    @classmethod
    def load(cls,path):
        return cls(json.loads(Path(path).read_text(encoding='utf-8')))


def verify_representation(original,shared,work):
    """Compare complete ordered predicate and program structures, not examples."""
    model=SharedEnglishReasoner(shared)
    compared=set()
    def equivalent(source,index,target):
        key=(id(source),index,target)
        if key in compared:return True
        compared.add(key);work.add('verified_predicate_nodes')
        a,b=source[index],shared['nodes'][target]
        if 'feature' not in a:return b==['ports',a['ports']]
        return (b[0]=='branch' and b[1]==a['feature']
                and equivalent(source,a['yes'],b[2]) and equivalent(source,a['no'],b[3]))
    for name in ('relevance','operations','program_router'):
        if original[name] is None:
            if shared['roots'][name] is not None:return False
        elif not equivalent(original[name],0,shared['roots'][name]):return False
    if set(original['programs'])!=set(shared['programs']):return False
    for name,entry in original['programs'].items():
        restored=model.programs[name]
        work.add('verified_programs')
        if entry['arity']!=restored['arity'] or tuples(entry['program'])!=restored['program']:
            return False
    return True
