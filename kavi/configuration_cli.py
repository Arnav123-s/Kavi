"""Query saved arithmetic connections and composed configurations."""

import argparse
import json
from pathlib import Path

from .configuration_composition import ArithmeticBridge, GraphCatalog
from .procedure_core import ProcedureLibrary

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='mode', required=True)
    bridge_parser = sub.add_parser('bridge')
    bridge_parser.add_argument('left', type=int)
    bridge_parser.add_argument('right', type=int)
    bridge_parser.add_argument('tokens', nargs='*')
    graph_parser = sub.add_parser('graph')
    graph_parser.add_argument('name')
    graph_parser.add_argument('values', type=int, nargs='+')
    args = parser.parse_args()
    library = ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json')
    try:
        if args.mode == 'bridge':
            bridge = ArithmeticBridge.decode((ROOT / 'experiments/mechanism-20260907-bridge.json').read_bytes())
            result = bridge.answer(args.tokens, (args.left, args.right), library)
        else:
            catalog = GraphCatalog.decode((ROOT / 'experiments/mechanism-20260907-catalog.json').read_bytes())
            execution = catalog.execute(args.name, args.values, library)
            result = {'state': 'answered', 'value': execution.value, 'calls': execution.calls,
                      'gates': execution.gates, 'iterations': execution.iterations}
    except ValueError as error:
        result = {'state': 'rejected', 'reason': str(error)}
    print(json.dumps(result))


if __name__ == '__main__':
    main()
