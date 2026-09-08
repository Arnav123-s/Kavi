# Learning English connections that construct answers

Author: [Arnav123-s](https://github.com/Arnav123-s)

Course recorded on 7 September 2026. Preparation was paused for the [design alignment audit](DESIGN_ALIGNMENT_AUDIT.md), then teaching was authorized to resume. The first run will learn routing connections and construct finite programs for supported quantitative questions. No score is claimed before the run. This tests one limited language skill; it does not implement the integrated learner or the wider subject curriculum.

## Retained state and input activity

An input supplies tokens, quantity positions and temporary values. Learned predicate connections route each pair of quantities toward an ordering of arithmetic operation ports. Where several interpretations remain possible, a bounded search constructs candidate expression trees and ranks their connection agreement. The selected tree becomes an executable configuration of the same kind as the acquired scientific calculations.

The deployed English artifact contains only predicate nodes, branch destinations and ordered operation ports. It contains no teaching question, worked answer, source paragraph, dictionary, example frequency or answer cache. Quantity values live only in the current invocation. Teaching records remain outside the model for reproducibility. The public learned arithmetic and science dependencies contain programs, not lists of taught numerical equations.

The retained configuration is still information and occupies bytes. Temporary activation also uses memory. Changing its representation cannot provide zero-space memory. Nor does removing raw examples prove absence of memorization: a large decision structure can overfit. Report training, development and frozen test results separately.

## Data and partitions

Use [ASDiv V1.0](https://github.com/chaochun/nlu-asdiv-dataset), by Shen-Yun Miao, Chao-Chun Liang and Keh-Yih Su, under CC BY-NC 4.0. The [authors' paper](https://aclanthology.org/2020.acl-main.92/) describes collecting website problems, editing repetitive language, manually annotating the equations and checking the answers. This course introduces no generated questions or altered-number teaching variants. The source XML has SHA-256 `ef8904068482919ac48c8eeaaf6df344b8a308ba66d048c2d4d87eab82dc4929`.

Exclude the four worksheet-generator source groups CommonCoreSheets, DadsWorksheets, Math-Aids and MathWorksheets4Kids from teaching and evaluation in this course. This is a conservative source selection; the remaining examples are published, manually reviewed corpus entries, not a guarantee about every upstream website's authorship process. Keep their original source IDs. Do not count those excluded groups as learner failures.

The first executable grammar supports two to five explicit quantities, each used once, joined by addition, subtraction, multiplication or division. Parse only the authors' formula to annotate the teaching connections. Missing constants, repeated quantities, extra irrelevant quantities and other operations remain outside this first grammar. Publish their counts and include them in a conservative full-admitted-corpus denominator. Do not hide them in the successful subset.

Group literal question templates after normalizing numbers and personal-name-like capitalization. Use SHA-256 of the normalized question to assign a fixed 60/20/20 train/development/test split. Neither answers nor formula operators determine that assignment. Record overlapping signatures and exact input hashes. The split is a project split, not the published ASDiv benchmark split. It does not guarantee that paraphrases are independent.

## Acquisition and search

For each published teaching expression, the lowest common ancestor of a pair of quantities supplies its operator and direction. A discrete classification tree learns which language predicates route to each operator ordering. The splitter, token/number parser, predicate inventory and search algorithm are supplied. No dense numerical weight array is learned. Temporary class frequencies choose the topology and port order, then are removed from the saved model.

This decomposition is related to [Roy and Roth's expression-tree approach](https://aclanthology.org/D15-1202/). The present implementation uses a simple predicate tree and a bounded composition search. It does not reproduce their entire system, solve general English or establish a new semantic-parsing method.

Declare three depth limits, 8, 12 and 16, with a minimum of three teaching connections per child. Select depth using only development answer accuracy. All runs use the same admitted teaching examples. Test the selected frozen model once. A later repair informed by test errors requires a new named evaluation; the first score is permanent.

For a candidate expression $E$, let $o_E(i,j)$ be the operation and direction at the lowest common ancestor of quantities $i,j$. Let $r_{ij}(o)$ be its position in the activated operation-port ordering. The supplied search controller ranks expressions by

$$S(E)=-\sum_{i<j}r_{ij}(o_E(i,j)).$$

This is a preference score, not a calibrated probability or a proof. Keep up to six candidate trees per quantity subset; compare with a width-one search and a language-blind operator ordering. Exhaust all binary partitions within that beam. Reuse partial computations. Charge every proposed configuration, invalid arithmetic operation, training predicate test and active connection.

Evaluate final answers by executing the constructed configuration, without passing the reference answer or formula to the answerer. Report top-one accuracy. An alternative containing the right number is diagnostic only; it does not count as an answered question. Give tentative answers through the interface instead of silently treating their interpretations as verified.

## Limits and live controls

Use one visible worker, a five-minute budget, a 512 MiB observed worker ceiling and Pause/Resume/Stop. Bound each search and learning call. Preserve all failure records, configuration sizes, run workspace bytes, model/source hashes and timings. Existing scientific retention checks remain separate from the new English test.

The user's private questions remain hidden and are not requested again. This finite course tests learned quantitative language and novel program construction. Broad physical explanation, dialogue, analogy, causal discovery and general language competence remain separate requirements unless measured.
