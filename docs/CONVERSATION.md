# Talking to Kavi

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [new English and direct-state courses](../experiments/2026-09-07-incremental-inquiry-transfer.md) are separate from the interface described here. This older window does not automatically load their artifacts or acquire their question policy. Its arithmetic and supplied equation handling do not demonstrate learned algebraic understanding.

The local conversation interface connects acquired arithmetic, the corrected scientific configuration, a restricted inequality pathway, a source passage index and an English lexical database. It responds to free text, but does not yet understand arbitrary wording or answer arbitrary questions reliably.

This interface is an auxiliary demonstration. It does not meet the project's intended learning architecture: conversational corrections do not change the persistent model, and source retrieval is not acquired semantic understanding. The [design alignment audit](DESIGN_ALIGNMENT_AUDIT.md) specifies that gap and the required configuration-replacement learning cycle.

```powershell
python -B -m kavi.conversation_window
python -B -m kavi.conversation "What is 2 plus 2?"
python -B -m kavi.conversation "Kinetic energy for mass 80 kg and speed 2.4 m/s"
python -B -m kavi.conversation
```

The last command opens a terminal conversation. Use `/quit` to finish. The window has Stop and Pause/Resume controls. `Show reasoning / source` explains the last calculation or source lookup. Conversations are not written to the public repository. No background training service is installed.

## What supplies an answer

| Route | What it does | What is learned |
| --- | --- | --- |
| Natural-number arithmetic | Executes acquired addition, subtraction and multiplication programs | Retained gates and procedure configurations |
| Fractions, real values, functions | Uses bounded supplied numerical operations | These adapters are engineered |
| Scientific calculation | Resolves quantity dependencies and invokes acquired configurations | Numerical program arrangements; quantity names, units and bindings are supplied |
| Radius inequality | Computes a strict upper bound under stated physical assumptions | Numerical subconfigurations from one published correction; proof rule supplied |
| Source passage | Ranks actual passages and returns an attributed excerpt | An explicit index of source text; no new general reasoning claim |
| Dictionary meaning | Looks up real WordNet senses, preserving alternatives | Imported lexical knowledge; no generated teaching pairs |

The arithmetic parser uses a restricted syntax tree, never `eval`. Inputs have size, nesting, exponent, work and numerical-range limits. A failed calculation is shown as unsupported. Unknown prose questions do not receive fabricated answers. The interface supplies greetings and status wording. That wording is software behavior, not a training corpus.

Scientific prompts should name the quantities, for example `heat for mass 2 kg, specific heat 4200, temperature rise 3`. Calculations use SI units unless a supported conversion is explicit. Supported conversions include grams/milligrams, centimetres, mph, km/h, kW, kJ, minutes and hours. This is not a complete dimensional-analysis parser. Inspect the interpreted quantities if a question is ambiguous.

## Data and provenance

No generated teaching examples are added after the owner's source-only instruction. Earlier experiments used generated numeric examples and retain that label. Later scientific lessons use identified published problems and annotated worked quantities. Source passages are copied from their actual institutions or original-work editions; no generated summaries or fabricated question-answer pairs enter the source index.

The corpus includes NHGRI genetics, USGS earthquakes and the water cycle, National Archives historical source text, official Python documentation, selected NASA passages and Plato/Aristotle in named English translations. These translations are not the Greek originals. The preceding scientific course inspected French Fourier, English Joule and German Einstein/Schrödinger; their prose was not learned as language. A small selection is not global historical coverage.

Local downloads that failed certificate validation remain recorded. Selected source text that was successfully inspected separately is labeled as selected text; it does not receive a raw-HTML hash. No TLS check is disabled. Source curation removes unrelated page notices, related-content panels, navigation and decoding defects. Textbook examination material is excluded from the prose index.

The optional dictionary is [WordNet 3.0](https://wordnet.princeton.edu/), distributed in the [NLTK data package](https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.xml). Its [license](https://wordnet.princeton.edu/license-and-commercial-use) and original copyright notice stay with the local copy. The parser reads noun, verb, adjective and adverb senses and uses the database's sense ordering. This is a lexical resource, not current factual coverage or a language model. A finite acquisition run is limited to five minutes, 512 MiB observed worker memory, a 20 MB download and 60 MB expanded archive. It does not extract arbitrary archive paths.

Source bodies, dictionaries, indexes and full transcripts remain in ignored `runs/` or `private/`. The public release contains code, model configurations, metadata and measured results. Model configuration bytes must not be reported as the size of this entire application: the lexical database, source index, interpreter, temporary indexes, interface and search work are additional resources.

## What the demonstration cannot establish

A relevant quotation may not answer the whole question. A dictionary sense is not an explanation of an unfamiliar argument. The language interface has no independently measured broad comprehension score, creativity score or graduate-level score. It does not silently call another model. The [experiment report](../experiments/2026-09-07-composable-science-and-conversation.md) separates calculation learning, source lookup, practice correction and fresh-question results.
