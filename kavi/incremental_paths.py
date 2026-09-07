"""Compile acquired sentence frames into a shared incremental state graph.

The graph keeps compatible interpretations open until further tokens or an end
marker resolve them. Shared states do not remove the cost of active bindings.
"""

import json
from .grounded_language import tokens


class IncrementalPaths:
    def __init__(self, rules):
        trie = {'edges':{}, 'accept':[]}
        for rule in rules:
            node = trie
            for item in rule['pattern']:
                key = ('literal',item) if isinstance(item,str) else ('slot',item['slot'],item['type'])
                node = node['edges'].setdefault(key, {'edges':{}, 'accept':[]})
            meaning = {'kind':rule['kind'],'label':rule['label']}
            if meaning not in node['accept']:
                node['accept'].append(meaning)
        self.nodes = []
        interned = {}
        def intern(node):
            edges = [{'match':list(key),'next':intern(child)} for key,child in sorted(node['edges'].items())]
            value = {'edges':edges,'accept':sorted(node['accept'],key=lambda x:(x['kind'],x['label']))}
            key = json.dumps(value,sort_keys=True)
            if key not in interned:
                interned[key] = len(self.nodes)
                self.nodes.append(value)
            return interned[key]
        self.root = intern(trie)
        self.reset()

    def reset(self):
        self.active = [(self.root,{},None)]
        self.input_tokens = []

    def feed(self, token):
        if not isinstance(token,str) or len(tokens(token))!=1 or tokens(token)[0]!=token:
            raise ValueError('Supply one normalized token')
        if len(self.input_tokens)>=96:
            raise ValueError('Input-token limit reached')
        self.input_tokens.append(token)
        following = []
        def advance(node_id,bound):
            for edge in self.nodes[node_id]['edges']:
                match, destination = edge['match'],edge['next']
                if match[0]=='literal':
                    if token==match[1]: following.append((destination,bound,None))
                elif match[2]=='natural':
                    if token.isascii() and token.isdigit():
                        following.append((destination,{**bound,match[1]:int(token)},None))
                else:
                    following.append((destination,{**bound,match[1]:token},match[1]))
        for node,bound,open_slot in self.active:
            if open_slot:
                following.append((node,{**bound,open_slot:bound[open_slot]+' '+token},open_slot))
            advance(node,bound)
            if len(following)>10000:
                raise ValueError('Active-binding limit reached')
        self.active = list({json.dumps(state,sort_keys=True):state for state in following}.values())
        return self.status()

    def status(self):
        meanings = {}
        labels = set()
        visited = set()
        def reachable(node):
            if node in visited: return
            visited.add(node)
            labels.update(x['label'] for x in self.nodes[node]['accept'])
            for edge in self.nodes[node]['edges']: reachable(edge['next'])
        for node,bound,_ in self.active:
            reachable(node)
            for accepted in self.nodes[node]['accept']:
                meaning = {**accepted}
                if accepted['kind']=='calculation':
                    meaning['inputs'] = [bound[f'n{i}'] for i in range(len(bound))]
                else: meaning['slots'] = bound
                meanings[json.dumps(meaning,sort_keys=True)] = meaning
        return {'possible_roles':sorted(labels), 'active_bindings':len(self.active),
                'active_nodes':sorted({x[0] for x in self.active}),
                'complete':list(meanings.values())}

    def finish(self):
        result = self.status()
        count = len(result['complete'])
        return {**result,'state':'interpreted' if count==1 else 'ambiguous' if count else 'unsupported',
                'original_tokens':list(self.input_tokens)}

    def encoded(self):
        return (json.dumps({'schema':'kavi.incremental-paths.v1','root':self.root,'nodes':self.nodes},
                           sort_keys=True,separators=(',',':'))+'\n').encode()
