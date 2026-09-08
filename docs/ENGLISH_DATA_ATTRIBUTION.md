# English experiment data attribution

Author: [Arnav123-s](https://github.com/Arnav123-s)

The English experiments use human-authored source problems and their published annotations. The data files and original licenses remain in local source folders. The public artifacts contain acquired predicates and variable-input programs, not copies of the questions or worked answers.

**ASDiv V1.0:** Shen-yun Miao, Chao-Chun Liang and Keh-Yih Su, [A Diverse Corpus for Evaluating and Developing English Math Word Problem Solvers](https://aclanthology.org/2020.acl-main.92/), ACL 2020, pages 975–984. The [author repository](https://github.com/chaochun/nlu-asdiv-dataset) distributes the dataset under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). The Kavi artifacts derived from this course retain that attribution and noncommercial restriction. Kavi's use excludes four source groups, applies the documented partitions, converts annotated calculations to variable-input programs, and learns routing predicates. It does not imply endorsement by the dataset authors.

**GSM8K base:** Karl Cobbe and coauthors, [Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168), 2021. The [OpenAI source repository](https://github.com/openai/grade-school-math) distributes the base files under its [MIT license](https://github.com/openai/grade-school-math/blob/master/LICENSE). The experiments use human-written base problems and solutions. Generated Socratic and model-solution files are excluded. Adding this source does not remove the ASDiv restrictions from a combined artifact.

The affected published artifacts are [the initial English configuration](../experiments/english-20260907-initial-model.json), [the expanded configuration](../experiments/english-20260907-expanded-model.json) and [its shared representation](../experiments/english-20260907-shared-model.json). The [experiment report](../experiments/2026-09-07-published-english.md) records source hashes, transformations, exclusions and measurements. Project authorship identifies Kavi's engineering and reporting; source authorship remains with the original authors.
