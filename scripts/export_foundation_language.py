"""Publish authored sentence frames while keeping source-derived memory local."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kavi.grounded_language import LanguageModel


def main():
    local = LanguageModel.load(ROOT / 'runs/foundation-checkpoint-20260907-03/language.json')
    public = LanguageModel(prefer_specific=local.prefer_specific)
    public.rules = [rule for rule in local.rules
                    if all(source.startswith('authored:') for source in rule['sources'])]
    destination = ROOT / 'experiments/foundation-language-20260907.json'
    destination.write_bytes(public.encoded())
    print(f'Published {len(public.rules)} authored frames in {len(public.encoded())} bytes; lexical memory and definitions remain local.')


if __name__ == '__main__':
    main()
