"""Query a saved recurrent configuration without its teaching data."""

import argparse
from pathlib import Path

from .recurrent_configuration import Configuration


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tokens', nargs='*', help='Space-separated a, b, ?a or ?b tokens')
    parser.add_argument('--model', type=Path, default=Path(__file__).resolve().parents[1] /
                        'experiments/recurrent-20260907-model.json')
    parser.add_argument('--trace', action='store_true')
    args = parser.parse_args()
    graph = Configuration.decode(args.model.read_bytes())
    if args.trace:
        for step in graph.trace(args.tokens):
            print(f"{step['token']}: state {step['from']} -> {step['to']}; "
                  f"output {step['output']}; revisited {step['revisit']}")
    prediction = graph.predict(args.tokens)
    print('unresolved' if prediction is None else prediction)
    return 0 if prediction is not None else 2


if __name__ == '__main__':
    raise SystemExit(main())
