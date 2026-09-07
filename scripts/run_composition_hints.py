"""Teach component-family hints, then evaluate a new number range."""

import argparse
from pathlib import Path
from scripts.run_foundation_curriculum import run


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_composition_hints','Teaching which component families to consider')
        return 0
    return run(args.run_dir,call_only=True,teacher_hints=True)


if __name__=='__main__': raise SystemExit(main())
