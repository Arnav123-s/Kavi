# Composition, scientific lessons and conversation

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Report of four completed local experiments and the subsequent source interface. [Measurements](2026-09-07-composable-science-and-conversation.json) contain source fingerprints, configurations, search counts and resource records. The [design alignment audit](../docs/DESIGN_ALIGNMENT_AUDIT.md) explains why these extensions do not yet constitute the intended integrated learner.

## Results

| Experiment | Result | What was supplied |
| --- | --- | --- |
| Local completion | 128/128 fresh inputs; 338 candidates in each condition; kernel calls reduced from 1,272 to 932 | The outer computation and boundary of its missing call |
| Correction and expansion | Corrected expansion 128/128; deliberately stale expansion 0/128 | Search procedure and dependency-invalidation checks |
| Polynomial differentiation | 128/128 numerical checks | The chain/product-rule transformation |
| Heat and two-state evolution | Each selected composition passed 128/128 fresh cases with one evolution call per case | The physical evolution kernels and restricted candidate grammar |
| Original-source numerical course | 13/13 practice targets and 1,152/1,152 generated transfer cases | Mathematical annotations, quantity roles, relations and real arithmetic |
| First independent textbook examination | 0/8 numerical targets; no complete problem solved | Structured inputs, units and explicit target quantities |
| Published worked lessons | Corrected practice 8/8; earlier practice retained 13/13 | Intermediate skill selection, numerical annotations and added semantic relations |
| Fresh textbook questions after correction | 4/5 annotated numerical targets | Same structured interface; fresh questions from the correction textbook |
| Radius-bound correction | Previously missed bound corrected; 17/17 earlier checks retained | Physical assumptions and inequality derivation |
| Conversation | Calculations, passage ranking and dictionary lookup available | Parsing, quantity interpretation and response behavior; no broad-language score |

The original-source numerical course used generated numerical teaching examples before the source-only instruction. The later published course used real question quantities and annotated worked steps. The distinction remains part of the record.

## Shared configurations and local completion

Primitive kernels, wires and hierarchical call arrangements use the same acyclic configuration interface. Definitions can be shared while invocations retain their own temporary values. This implementation has one output per configuration, supplied kernel semantics and explicit execution limits. It does not implement general recurrent relational activity or learned scheduling.

The outer computation is supplied. It adds two inputs, passes that intermediate and a third input into a missing call, and adds a fourth input to the result. Four teaching examples constrain the final answer to (x+y+z) squared plus w. The learned missing call adds its two inputs and multiplies that sum by itself.

Both search conditions enumerate 338 candidates. The whole condition recomputes the outer graph; the local condition preserves known prefix values only during that teaching transaction. Kernel calls fall by 340, or 26.73%. Neither condition learns the location of the missing computation. The accepted arrangement passes 48 promotion and 128 final cases. The earlier addition and multiplication operations pass 512 retention checks.

~~~mermaid
flowchart LR
    X[First two inputs] --> A[Acquired addition]
    A --> H[Learned missing configuration]
    Z[Third input] --> H
    H --> B[Acquired addition]
    W[Fourth input] --> B
    B --> O[Output]
    subgraph Hinside[Inside the missing configuration]
        S[Add its inputs once] --> M[Multiply the sum by itself]
    end
    H -. expanded view .-> Hinside
~~~

The provisional correction lesson (2,2) giving 4 admits 104 candidate configurations. The selected initial graph computes twice its first input; on (2,3), it returns 4. Further correction selects multiplication. An expanded computation bound to the earlier definition is rejected as stale. Rebuilding it gives 128/128 correct final answers; bypassing the guard gives 0/128 on that bank. This tests propagation of a changed definition, not unrestricted semantic correction.

The differentiation transformer expands an acquired polynomial configuration and applies supplied chain and product rules. Its numerical checks pass 128/128. The learner did not discover calculus from the source material.

## Equation compositions

The supplied heat kernel describes three fully coupled temperatures in normalized units:

$$T_i(t)=\bar T+\exp(-3t)(T_i(0)-\bar T),\qquad t\geq0.$$

The supplied quantum kernel uses a two-state system with hbar equal to one and a fixed Hamiltonian:

$$H=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad U(t)=\cos(t)I-i\sin(t)H.$$

For each kernel, the learner evaluates 154 candidates and selects a composition that adds two equal time intervals, then invokes evolution once. Each passes 48 promotion and 128 fresh cases. The experiment tests the same fixed dynamics with two equal consecutive intervals, not arbitrary time-dependent physical systems.

Evolution calls decrease from 256 to 128 on each final bank, but the selected computation adds 128 arithmetic calls. Total kernel calls remain 256. The physical-kernel cost of 12 units and arithmetic cost of one unit are supplied accounting estimates, not measured CPU instructions. Single sub-millisecond or millisecond timings do not establish a general speed advantage.

The heat checks found no range violation and at most approximately 1.14e-13 error in conserved temperature sum. Quantum normalization error was at most approximately 4.44e-16. A separate phase diagnostic produced populations approximately zero and one for two coherent inputs, whereas discarding phase predicts one half for each. These are classical calculations of a tiny quantum system; they are not quantum hardware or demonstrated improvements to general learning.

## Scientific teaching and textbook transfer

The first course used interpretations of Fourier in French, Joule in English, and Einstein and Schrödinger in German. The [protocol](../docs/SCIENTIFIC_CURRICULUM_PROTOCOL.md) identifies inspected editions and passages. The actual numerical learner received annotated inputs and outputs. It did not read the prose, discover its vocabulary or derive the physical meaning of its quantity labels.

Nine numerical families were taught. The final banks contain 168 examples; the two rounds present 192 examples in total because earlier examples are used again. After teaching, the thirteen OpenStax practice targets pass. Nine generated transfer banks of 128 cases each also pass. Repeating those banks after the structural-sharing pass checks retention on the same cases; it is not another set of 1,152 unseen questions. The pass finds no duplicate definitions to consolidate, so the artifact remains 4,205 bytes. Earlier composition checks pass 256/256.

The model is frozen before the next textbook examination. The examination uses five consecutive problems, 7-d6 through 7-d10, from Crowell and Shotwell's [Problems in Introductory Physics](https://www.lightandmatter.com/problems/problems.pdf), with eight scored numerical targets. Problems 7-d7 and 7-d10 acknowledge Arnold Arons. All eight targets are initially unresolved, and qualitative subparts are unsupported.

The correction course uses sixteen annotated worked quantities from these published questions and problems 7-a1 and 7-m6. It learns seven program arrangements after 11,725 candidate proposals. Half, double, square root and cube root are supplied numerical kernels. Seventeen additional quantity relations are supplied in the teaching interface. The acquired programs correct all eight practice targets; thirteen older numerical targets still pass, and all 31 earlier definition records remain unchanged.

After freezing the 7,025-byte model, five fresh targets from problems 7-m1 through 7-m5 score 4/5:

| Problem | Target | Result |
| --- | --- | --- |
| 7-m1 | Speed after a fall and heat loss | Correct |
| 7-m2 | Electrical cost | Correct |
| 7-m3 | Lifting power | Correct |
| 7-m4 | Lifting duration | Correct |
| 7-m5 | Radius inequality | Unsupported |

This is an independent textbook relative to the earlier OpenStax practice. The fresh set after correction comes from the same Crowell/Shotwell book as the correction lessons; it is not a third independently sourced examination. Explicit given quantities and targets replace raw-language interpretation in every scored case. The observed 4/5 result cannot be described as an English-reading or graduate-physics score.

## Correction of the remaining inequality

Problem 7-m5 becomes a practice correction after its failure has been recorded. Three learned scalar subcomputations and a supplied wrapper compute the upper bound. The teaching interface supplies the reasoning: starting from rest with strictly positive frictional loss, a circular crest, positive gravity and the declared normal-force fraction implies

$$0<r<\frac{2(h_0-h_1)}{1-f},\qquad h_0>h_1\geq0,\quad 0\leq f<1.$$

For the problem's quantities, the strict upper bound is 72 metres. The interface rejects missing premises or values outside its domain. Four earlier fresh numerical questions and thirteen older practice targets still pass: 17/17 retention checks.

No new unseen inequality question has been tested. The earlier examination stays 4/5. This correction is not an independently learned physical proof or evidence that arbitrary inequalities now work. The [correction protocol](../docs/PUBLISHED_BOUND_CORRECTION.md) records the premises and scope.

## What the conversation extension adds

The interface connects learned calculations to a supplied parser, a curated passage index and WordNet 3.0. The local source index contains 24 documents and 700 passages in 120,708 serialized bytes. The dictionary contains 147,306 lexical entries and 117,659 senses; its archive occupies 10,775,600 bytes and its expanded members total 36,353,991 bytes. These entries and passages are retrieved information, not that many acquired concepts.

Source material includes NHGRI, USGS, the National Archives, official Python documentation, selected NASA text and named English translations of Plato and Aristotle. Those translations are not the Greek originals. The selection is not comprehensive across traditions and periods.

An initial acquisition attempted 29 documents and obtained 16; thirteen failures remained recorded. Some downloads failed certificate validation. Separately inspected passages were later stored as selected text, with their own provenance, rather than being labeled successful raw-page downloads. No certificate validation was disabled.

Curation removes navigation, unrelated notices, related-content panels, duplicate paragraphs and decoding defects. Early relevance probes exposed poor matches. These are retrieval-engineering observations, not a scored language benchmark. A source excerpt can still be irrelevant or incomplete as an answer.

The conversation application does not change its persistent configuration when corrected. It does not use another language model to supply answers. Its free-text input, greetings, arithmetic parsing and quantity interpretation are supplied software. The [interface reference](../docs/CONVERSATION.md) describes usage and the [alignment audit](../docs/DESIGN_ALIGNMENT_AUDIT.md) records the architectural mismatch.

## Resources and artifacts

| Run | Wall seconds | CPU seconds | Display pacing seconds | Peak worker bytes | Recorded local run bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hierarchical configurations | 20.093 | 0.328 | 19.798 | 27,250,688 | 106,056 |
| Scientific course | 19.904 | 0.547 | 19.490 | 26,939,392 | 220,319 |
| Published corrections and examination | 21.775 | 0.453 | 21.323 | 26,415,104 | 48,383 |
| Inequality correction | 6.088 | 0.109 | See measurements | 26,611,712 | 25,451 |

The display is a separate process, excluded from the worker peak. Local run bytes come from each recorded census and exclude that census file. No CPU-temperature measurement was available. All four runs used finite controls, with a five-minute wall budget and a 512 MiB observed worker ceiling. Counted work limits and constituent fields are in the protocols and measurements.

| Saved configuration | Bytes |
| --- | ---: |
| [Hierarchical laboratory model](composable-20260907-model.json) | 1,894 |
| [First scientific freeze](science-20260907-initial-model.json) | 4,205 |
| [Published-lesson freeze](science-20260907-published-model.json) | 7,025 |
| [Radius-bound extension](science-20260907-radius-bound.json) | 3,980 |

The earlier [compiled arithmetic library](library-20260907-compiled.json) occupies 2,272 additional bytes. The latest science model includes earlier hierarchical definitions; summing all historical checkpoints does not describe its deployed size. The science model, arithmetic dependency and bound extension together occupy 13,277 serialized bytes. Runtime code, source lookup, dictionary data, temporary indexes, working values and training/search storage are additional resources.

Source bodies, teaching records and full transcripts stay local. The public summary preserves measurements and hashes, while the exported inference artifacts contain configurations and dependency metadata. Protocols may have later status annotations; recorded run fingerprints identify the versions used at execution.

## Verification and current direction

The implementation regression suite passed 233 tests before the design audit. Publication checks cover the exported models, relevant inference paths, documentation references and diagram syntax. Regression fixtures are engineering checks, not additional teaching data or a general-intelligence benchmark.

At the time of these four science and composition runs, the English prototype had not been taught. Subsequent [published English courses](2026-09-07-published-english.md) and [incremental correction and direct state learning](2026-09-07-incremental-inquiry-transfer.md) have separate measured records. The broader requirement remains to connect interpretation, construction and correction in a useful configuration-learning cycle. Increasing a retrieval corpus does not establish that capability.
