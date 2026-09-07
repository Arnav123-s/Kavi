# Kavi among learning systems: representation, size and capability

Author: [Arnav123-s](https://github.com/Arnav123-s)

Revision: 7 September 2026

This comparison covers the principal model families and the closest structural-learning relatives. It is a taxonomy and storage analysis, not an exhaustive inventory of every published architecture or a new benchmark. Sources are original papers, author publications and official implementation documentation. Named model releases are reference points, not a ranking of the latest systems.

## Finding

Kavi's current 2,238-byte retained artifact belongs to the small executable-program end of machine learning. It is much smaller than a language-model parameter array, but it has a much narrower interface and demonstrated capability. Small statistical models, formulas and synthesized programs can be smaller still. No equal-capability storage advantage over those systems has been measured.

The implemented learner selects discrete gates, connections and compositions from formal examples. Its closest description is bounded typed program induction over acquired finite-state transducers. Its broader proposed architecture adds adaptive shared structure, repair and abstraction discovery; those features must not be credited to the present implementation before they work.

The important distinction is what gets retained. Conventional neural models predominantly retain numerical tensors. Kavi retains an executable description. Both are persistent information. The absence of numerical edge weights does not imply the absence of parameters in the broader sense: gate choices, connection addresses, constants, types and procedure bodies are learned or supplied configuration.

## What counts as model size

| Quantity | What it includes | Current evidence |
| --- | --- | --- |
| Saved learned artifact | Canonical program library, names, types, gates and connections | 2,238 bytes; 13 procedures |
| Execution implementation | Code that gives the saved instructions meaning | The two core source files total 19,100 bytes; this is a partial source inventory, not a standalone executable size |
| Runtime memory | Loaded program, Python objects, integer values, stack and temporary state | Inference-only peak has not been separately measured |
| Learning process memory | Runtime plus candidate search, teaching and evaluation work | Recorded worker peaks of 46.70 and 47.92 MiB in the two trials |
| External evidence | Sources, examples, audits and detailed run files | About 20.1 and 20.7 decimal MB of run files at the prior audit; source storage is separate |
| Capability | Tasks solved under declared inputs, accuracy and resource limits | Elementary natural-number procedures; no prose comprehension or graduate subject assessment |

The core source files are `kavi/circuit_core.py` (6,679 bytes) and `kavi/procedure_core.py` (12,421 bytes), measured on this revision. Python, its standard library, packaging and command interfaces are additional dependencies. Source-file bytes are not RAM or compiled binary bytes. Neither they nor learning memory should be silently included in one competitor's model size and excluded from another's.

The retained library was assembled from compatible acquired procedures from two runs; it is not the output of a single autonomous consolidation run. Exact boundaries and failures are in the [experiment record](../experiments/2026-09-05-procedure-library.md).

## Statistical, instance-based and probabilistic models

The size relations below describe common representations, excluding file headers and software dependencies. Let d be the number of input features, c the number of classes, n the number of retained examples, k a chosen component count, and b the bytes per stored number. These relations are engineering derivations from the cited representations, not measured file sizes.

| Family | What learning retains | Difference from Kavi and storage consequence |
| --- | --- | --- |
| Linear and logistic models, ridge and lasso | Coefficients and intercepts | They fit a specified numerical function. A scalar linear model needs about b(d+1) bytes and can be smaller than Kavi. Sparsity may reduce coefficients but adds indices. [Reference](https://scikit-learn.org/stable/modules/linear_model.html) |
| Naive Bayes | Class priors and feature statistics | It models class-conditional evidence rather than an executable arithmetic procedure. Common variants need O(cd) statistics and can be very small. [Reference](https://scikit-learn.org/stable/modules/naive_bayes.html) |
| Decision trees and rule systems | Tests, thresholds, branches and output values | Already a form of learned routing. A tree partitions input regions; Kavi composes and repeats acquired operations. Storage grows with nodes and leaf values, not a compulsory dense weight matrix. [Reference](https://scikit-learn.org/stable/modules/tree.html) |
| Random forests, boosting and other ensembles | Multiple component models and combination rules | Aggregate storage is roughly the sum of their components. They can be compact or large; there is no family-wide byte count. [Reference](https://scikit-learn.org/stable/modules/ensemble.html) |
| Nearest neighbors and prototypes | Examples, labels or representative points, sometimes an index | Typical exact nearest-neighbor storage grows with nd. Kavi's deployed library does not look up its teaching examples. Prototype compression trades coverage against representation size. [Reference](https://scikit-learn.org/stable/modules/neighbors.html) |
| Kernel SVMs | Support vectors, coefficients and kernel settings | Size depends on support-vector count, roughly O(sd) for s dense support vectors. A linear SVM can instead collapse to a coefficient vector. [Reference](https://scikit-learn.org/stable/modules/svm.html) |
| Gaussian processes | Kernel settings, conditioning data and often matrix factors | A small kernel parameter count does not describe the entire predictor. Exact implementations can retain O(n²) factors as well as data; approximations change this boundary. [Reference](https://scikit-learn.org/stable/modules/gaussian_process.html) |
| Clustering: k-means, density and hierarchical methods | Centers, exemplars, labels or structures, depending on method | A k-means predictor may need only kd numbers. Other clustering methods have different deployment interfaces; some have no ordinary unseen-point prediction operation. [Reference](https://scikit-learn.org/stable/modules/clustering.html) |
| PCA, NMF and factor models | Bases, means, factors or entity embeddings | PCA with k components needs roughly kd coefficients plus centering. Retained training factors or recommendation embeddings add storage. These represent structure numerically rather than as callable algorithms. [Reference](https://scikit-learn.org/stable/modules/decomposition.html) |
| HMMs and related probabilistic state models | Transition and emission distributions | An HMM with k states has a transition table of order k², plus emissions. It represents uncertainty over states; Kavi's acquired arithmetic transducer is deterministic. [Reference](https://hmmlearn.readthedocs.io/en/0.3.3/tutorial.html) |

These families disprove the premise that all machine learning requires a large collection of neural weights. They also demonstrate that compactness alone is not a distinctive contribution.

## Neural and generative models

| Family | Retained and temporary state | Difference from Kavi and size implication |
| --- | --- | --- |
| Dense neural networks / MLPs | Layer matrices, biases and temporary activations | Fit distributed numerical computations. P stored parameters at q bits require approximately Pq/8 bytes before overhead. Kavi stores discrete instructions instead. [Implementation reference](https://scikit-learn.org/stable/supervised_learning.html) |
| CNNs and residual image networks | Shared convolutional filters and other layer parameters | Weight sharing already reuses one operation across positions. Their image capability is absent from Kavi; a small arithmetic library is not a replacement. [Compact CNN example](https://arxiv.org/abs/1602.07360) |
| RNNs, LSTMs and GRUs | Reused recurrent parameters and changing hidden state | A fixed parameter set can process varying sequence lengths. Reusing computation across inputs is therefore not exclusive to programs. [Recurrent formulation and variants](https://www.scholarpedia.org/article/Echo_state_network) |
| Transformers | Projection and feed-forward weights, embeddings; context-dependent attention and caches | Routing varies with the input even when long-term weights are fixed. Ordinary attention is not persistent rewiring. Stored weights and context memory are separate size quantities. [Original paper](https://arxiv.org/abs/1706.03762) |
| Mixture-of-experts networks | Router and expert parameters | Sparse activation reduces the work used for a token, not the total expert information that must be stored somewhere. Kavi's calls are explicit program composition. [DeepSeek-V3](https://arxiv.org/abs/2412.19437) |
| State-space models such as Mamba | Learned transforms and recurrent state | Input-dependent selection controls propagation while trained parameters remain. Efficient sequence state is a different claim from weight-free structural learning. [Original paper](https://arxiv.org/abs/2312.00752) |
| Graph neural networks | Message and update functions, usually numerical parameters | An input graph and a learned program graph have different roles. Neural message passing does not itself mean that reusable procedures are being invented. Graph storage must be counted separately. [Original framework](https://arxiv.org/abs/1704.01212) |
| Autoencoders and VAEs | Encoder/decoder parameters, latent representations | Learn reconstructions or distributions. Latents do not replace the decoder's storage. They address noisy, high-dimensional representation tasks that Kavi has not attempted. [VAE paper](https://arxiv.org/abs/1312.6114) |
| GANs | Generator and, during training, discriminator | A deployed generator can omit the discriminator. The training-system size and inference-model size differ, just as Kavi's search can be omitted from inference. [Original paper](https://arxiv.org/abs/1406.2661) |
| Diffusion models | Denoising network and any conditioning/encoding networks | Repeated sampling steps reuse parameters; the number of steps is not a multiplier on saved weights. Temporary execution cost can remain substantial. [DDPM paper](https://arxiv.org/abs/2006.11239) |
| Normalizing flows | Parameters of invertible transformations | Here “flow” means an invertible probability transformation. It is not automatic physical routing or a storage-free circuit. [Technical reference](https://arxiv.org/abs/1912.02762) |
| Binary, ternary and quantized networks | Low-precision numerical weights, scales and metadata | Removing most weight bits can shrink a network without changing it into a learned program library. Theoretical bits per weight are not necessarily the entire serialized model cost. [BitNet b1.58](https://arxiv.org/abs/2402.17764) |

Pruning, distillation, low-rank factorization and parameter sharing are compression or training strategies, not mutually exclusive model families. A size comparison must state the resulting representation. A sparse model may need connection indices; a distilled model retains a smaller student's parameters; a low-rank representation retains its factors. Kavi must be compared with compressed competitors as well as full-precision ones.

## The closest relatives to the original idea

| Approach | Shared idea | Material distinction |
| --- | --- | --- |
| Program synthesis and library learning | Retain reusable executable procedures | This is the closest category to implemented Kavi. DreamCoder also discovers abstractions and trains a neural search guide; Kavi presently uses a fixed enumerator and supplied instruction semantics. [DreamCoder](https://arxiv.org/abs/2006.08381) |
| Inductive logic programming | Learn reusable rules from examples and background knowledge | Systems such as Metagol can invent predicates and higher-order programs. Kavi currently has a narrower arithmetic grammar and different execution representation. [Original paper](https://www.doc.ic.ac.uk/~shm/Papers/metafunc.pdf) |
| Symbolic regression / genetic programming | Search for compact expressions or programs | A discovered formula can be far smaller than a neural approximation. PySR also optimizes numerical constants, whereas Kavi's present library uses supplied zero/one constants and acquired gates. [PySR](https://arxiv.org/abs/2305.01582) |
| Differentiable logic gate networks | Learn Boolean computation that can execute as gates | Very close at the gate layer. These systems use continuous relaxations during training; Kavi uses discrete candidate search. Gate-based inference is established prior work. [Original paper](https://arxiv.org/abs/2210.08277) |
| Recurrent differentiable logic networks | Combine logic gates with sequence state | Even recurrent Boolean learning has direct prior work. Its reported translation experiment is a separate task and does not establish superiority over Kavi. [2025 preprint](https://arxiv.org/abs/2508.06097) |
| WiSARD and other weightless networks | Avoid conventional multiply-accumulate weight layers | They retain lookup structures rather than Kavi's callable arithmetic programs. Weightless does not mean memoryless; memory requirements can be substantial. [BTHOWeN](https://arxiv.org/abs/2203.01479) |
| NEAT and topology evolution | Learn connectivity as well as behavior | NEAT evolves topology and weights. Kavi's current search selects discrete gates and wires without numerical edge training; structural search itself is not new. [Original paper](https://direct.mit.edu/evco/article/10/2/99/1123/Evolving-Neural-Networks-through-Augmenting) |
| Fast weights and plastic networks | Inputs change a computational state that acts like weights | Close to the “liquid weights” intuition. A slower learned controller usually remains, and the fast matrix is memory. Kavi's deployed program is currently unchanged by a query. [Fast weight programmers](https://arxiv.org/abs/2102.11174) |
| Hypernetworks | One mechanism generates another mechanism's weights | Generation can share or compress descriptions, but the generator still carries persistent parameters and the generated weights require execution space. [Original paper](https://arxiv.org/abs/1609.09106) |
| Liquid time-constant networks / neural differential equations | Input-driven changing dynamics | “Liquid” refers to dynamical behavior, not the disappearance of learned parameters. Kavi's current model is discrete and has no differential-equation solver. [LTC paper](https://arxiv.org/abs/2006.04439) |
| Reservoir computing / liquid state machines | Drive a recurrent medium with signals | Classical echo-state learning mainly trains a readout over a fixed reservoir. The reservoir and readout are still part of the implementation. [Author reference](https://www.scholarpedia.org/article/Echo_state_network) |
| Spiking networks | Signals propagate through event-driven circuits | Synaptic parameters and neuron state generally remain. Event-driven execution can affect energy and latency without implying compact learned programs. [Technical reference](https://arxiv.org/abs/1901.09948) |
| Retrieval-augmented systems | Reuse information outside a fixed predictor | Count the retriever, generator, index and corpus. Kavi's deployed library does not retrieve teaching examples; adding a source memory would change its accounting. [RAG paper](https://arxiv.org/abs/2005.11401) |

Supervised, unsupervised, self-supervised, reinforcement, online and meta-learning describe learning arrangements, not a unique byte layout. Reinforcement learning, for example, can retain a small action-value table or a neural policy. A program learner could also be optimized using rewards. Kavi's present formal-example search does not establish that implementation. [Sutton and Barto](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf)

Quantum-inspired routing is also a separate proposal. The current artifact is classical. A full state-vector simulation of n qubits uses 2^n complex amplitudes; special structures and approximation methods can change that expense. Imagining a circuit does not supply quantum hardware or an automatic compression advantage. [IBM Research](https://research.ibm.com/publications/a-compressed-classical-description-of-quantum-states)

## Numerical size comparisons

Use decimal kB/MB/GB below: 1 kB = 1,000 bytes. Kavi's 2,238 bytes are 2.238 kB or 2.186 KiB. All neural payload calculations exclude the executor, tokenizer, caches, training state, container metadata and quantization overhead. They are arithmetic comparisons, not downloaded file measurements or equal-capability evaluations.

| Reference representation | Payload assumption | Bytes | Relative to Kavi's saved artifact |
| --- | --- | --- | --- |
| Scalar linear model with 100 features | 101 FP32 numbers including bias | 404 | Kavi is about 5.5 times larger |
| A chosen 10,000-parameter neural model | FP32 | 40,000 | About 18 times larger |
| A chosen 1-million-parameter neural model | FP16 | 2,000,000 | About 894 times larger |
| Qwen2.5-0.5B | Approximate 0.49B published count, FP16/BF16 payload | 980,000,000 | About 438,000 times larger |
| A chosen 8-billion-parameter model | Ideal packed 4-bit payload | 4,000,000,000 | About 1.79 million times larger |
| The same 8-billion-parameter count | FP16/BF16 payload | 16,000,000,000 | About 7.15 million times larger |
| DeepSeek-V3 | 671B total parameters, hypothetical uniform 16-bit payload | 1,342,000,000,000 | About 600 million times larger |

Qwen's count is from its [official model card](https://huggingface.co/Qwen/Qwen2.5-0.5B). DeepSeek's [report](https://arxiv.org/abs/2412.19437) distinguishes 671B total parameters from 37B activated per token. The 1.342 TB row is a uniform-precision calculation, not its actual distributed checkpoint format or required active memory. The generic 10,000-, one-million- and eight-billion-parameter examples are chosen comparison points, not claims that every model in a family has that size.

One more useful reference is [SqueezeNet](https://arxiv.org/abs/1602.07360), whose authors reported a compressed image model below 0.5 MB. This demonstrates that compact neural models are established; its vision task and its compressed encoding differ from Kavi's.

The payload equation is:

```text
neural payload bytes = parameter count × bits per parameter / 8
```

Kavi's entire JSON file occupies the same number of bits as 1,119 FP16 values or 4,476 ideally packed four-bit values. This is a storage equivalence only. It is not a parameter count or a capability equivalence.

## Why addition is a necessary counterexample

For numeric inputs, addition has the linear form y = w1*a + w2*b + c, with w1 = w2 = 1 and c = 0. Those three FP32 values occupy twelve payload bytes. Thus a weight-based representation of the function can be smaller than Kavi's gate description. This is an analytical example, not a fitted or benchmarked baseline.

The representation boundary matters: that linear executor receives numeric operands and already implements multiplication and addition. Kavi's gate experiment starts with lower-level Boolean gates and streams bits. Ordinary floating-point linear execution also does not guarantee exact arbitrary-length integer arithmetic. A fair contest must align primitives, input representation, precision, output contract and execution budget.

Equally, a hand-written arithmetic routine can be very small, but its programmer supplied the solution. To evaluate learning, compare what each system inferred from the same evidence, what was built in, and how much work it required. Comparing tiny output programs while ignoring very different supplied operators can reverse the apparent result.

## What wiring costs

For an explicitly stored graph with V addressable nodes and E directed edges, a simple adjacency encoding needs on the order of E*log2(V) bits for edge targets, plus source organization, operation labels, constants and interfaces. Repeated or regular structures can be encoded more compactly by a generating rule. Random, irregular connections may not compress well.

Replacing a scalar edge coefficient with a connection choice trades one information encoding for another. It does not make the choice free. On physical hardware that choice may live in routing switches or fabrication; in software it lives in addresses or program instructions. A complete comparison therefore measures the encoded graph rather than declaring its parameter count to be zero.

Kavi's temporary carry state disappears after a query, while its program library persists. Persistent structure is a form of memory. A literally stateless learner, with no changed structure and no external state, could not behave differently tomorrow because of feedback received today.

## Where the idea could stand as it grows

The measured position is a compact specialist program learner. The plausible advantage is low additional description cost when a new task can call earlier procedures. The actual follow-up added 109–171 bytes per accepted procedure; a 113-byte scaling arrangement improved larger power and factorial execution. The same larger vocabulary also caused sum-of-squares search to time out. Storage and acquisition difficulty did not improve together in every task.

There is no evidence-based estimate for the size of a language-capable or broadly advanced Kavi. For arithmetic illustration only, one million procedures averaging 120 bytes would be 120 MB before extra indexing, literals or supporting components. Nothing in the current trial justifies either the million-procedure count or the constant 120-byte average. It is not a forecast of intelligence or an alternative to a billion-parameter model.

Short descriptions are possible for regular computations. Arbitrary facts, exceptions, images and noisy observations need not have that regularity. A fixed B-bit store has at most 2^B configurations. More independent information requires more storage, approximation, external memory or stronger assumptions. Neither routing nor reuse removes this limit.

The closest mathematical comparison is conditional program description length: how many extra bits describe a new task given an existing library? Neural representations also exploit shared structure, so the research question is comparative: which representation offers the best accuracy, coverage, learning cost and execution cost under the same constraints?

## The comparison that would establish an advantage

Start with the present arithmetic interface and freeze the task splits before fitting any competitor. Report separate conditions with numeric inputs and bit-stream inputs. Include a small linear baseline where its hypothesis class is relevant, a compact recurrent neural baseline, a differentiable logic learner, a symbolic/program learner and hand-written reference algorithms. The last group establishes execution cost, not learned capability.

For each condition record canonical learned bytes, supplied primitive definitions, full deployment dependencies, peak learning and inference memory, learning time, runtime, accuracy, resource failures and larger-input transfer. For neural methods include quantized variants where valid. For symbolic methods include serialization and shared-library choices. Do not score unsupported problems as absent from the test set.

Then add sequences, branching, graphs, noisy data and unfamiliar compositions. Measure whether newly acquired abstractions improve later tasks while older behavior remains correct. Plot storage against achieved capability at a fixed correctness threshold, rather than treating fewer bytes as an automatic win. A system that solves fewer tasks cannot claim better compression of the same knowledge.

No competing models were trained in this review. The present conclusion is therefore about representation and measured Kavi size: very small compared with neural language-model payloads, not uniquely small among machine-learning systems, and not yet shown to use less storage for comparable broad capability.
