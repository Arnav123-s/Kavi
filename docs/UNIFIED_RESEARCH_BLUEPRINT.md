# Kritjnah: unified research and algorithm blueprint

**Author:** Arnav123-s
**Research snapshot:** 2026-09-03
**Status:** design proposal; not implemented, trained, or validated

## 1. Executive answer

Kritjnah can be made into a rigorous local research system, but the physics
metaphors must become measured software variables rather than claims that
knowledge literally is mass, heat, gravity, light, or time. The strongest
implementable design is:

1. a compact recurrent or equilibrium-style learner;
2. an external evidence and hypothesis memory with complete provenance;
3. fast and slow learning channels protected by measured importance;
4. grow--learn--consolidate--compress cycles with retention gates;
5. a serial, bounded experiment harness that archives alternative designs;
6. a fixed evaluator and resource controller outside the editable surface;
7. formal verification, not model confidence, for mathematical proofs.

The two earlier research lists are not actually competing designs. The
physics/information list describes *what state should mean and how it should
behave*. The algorithm list describes *how to implement and test that behavior*.
The starred repositories add useful implementations for efficient inference,
self-research archives, Bayesian experiment selection, retrieval, differentiable
constraints, external memory, and reproducible benchmarking. No one source
provides the whole system.

The main unresolved scientific question is still the learning rule. This
blueprint allows conventional gradients, local gradients, reinforcement
estimators, and evolutionary search to be compared under the same evaluator.
It does not assume that removing backpropagation is itself an improvement.

“Self-improvement” has three different meanings and they must not be mixed:

- **Knowledge adaptation:** beliefs, memories, and weights change from evidence.
- **Architecture search:** bounded candidate architectures are trained and tested.
- **Source-code self-modification:** a later-phase generator proposes patches.

Only the first two belong in the initial experiments. Source-code mutation stays
locked until an external evaluator, isolated executor, immutable limits, rollback,
and explicit owner approval exist. Endless work means a supervisor can launch the
next bounded experiment after failures; it must never mean removing the kill
switch or letting the candidate rewrite its evaluator.

## 2. Evidence and scope

This document combines two prior Kritjnah research artifacts:

- the physics, information, thermodynamics, quantum, gravity, and time synthesis;
- the cross-field algorithm and software-method crosswalk.

It also audits all **13 repositories visible in the public starred list** of
`Arnav123-s` at the snapshot date. Private stars, if any, are not visible through
the public interface. For large repositories, the audit covered the README,
linked primary paper, repository structure, and the source paths implementing the
relevant algorithm. It is not a claim of line-by-line review of every file. The
two tiny algorithm repositories were inspected in full. Forks are listed but are
not double-counted as independent research.

Evidence labels used below:

- **Established:** supported by the cited work in its stated domain.
- **Implemented elsewhere:** source code exists, but not yet in Kritjnah.
- **Proposed:** a concrete Kritjnah adaptation that still needs an experiment.
- **Rejected initially:** scientifically unsupported, unsafe, or unsuitable for
  this device.

## 3. Comparison of the two research lists

| Physics/information idea | Engineering meaning | Existing algorithm family | Starred-repository support | Kritjnah decision |
|---|---|---|---|---|
| Knowledge as mass | Stable, useful structure resists destructive updates | EWC, synaptic intelligence, natural gradient | Theseus can express constrained objectives | Proposed as bounded **structural inertia**, never literal mass |
| Evidence as energy | An observation can change belief or allocate work | Bayesian/Kalman update, active learning | SustainableConcrete uses Gaussian processes and uncertainty-aware experiment selection | Use calibrated likelihood and expected information gain |
| Thought as heat | Uncertainty and disagreement increase exploration | Entropy, simulated annealing, prioritized replay | HyperAgents explores an archive; BOxCrete explores uncertain regions | Use a cognitive temperature distinct from hardware temperature |
| Gravity/binding | Related representations merge when joint coding saves resources | MDL, information bottleneck, clustering, distillation | Faiss supplies clustering/retrieval; BitNet supplies efficient representation | Compress only after capability and calibration tests pass |
| Different local times | Components update at different rates | Multi-timescale memory, adaptive computation, coordinate descent | RL-NTM demonstrates sequential controller/memory actions | Use per-group clocks plus one global ordered event log |
| Quantum alternatives | Preserve incompatible hypotheses until evidence separates them | Particle filtering, ensembles, query by committee | BOxCrete represents posterior uncertainty | Use classical probability; no simulated qubits initially |
| Quantum Darwinism | Confidence should depend on independent redundant records | Truth maintenance, provenance, source-dependence correction | Three Bricks illustrates statistical detection with controlled false positives | Count independent evidence, not repeated text |
| Renormalization | Replace detail with task-preserving coarse variables | Distillation, bottlenecks, multiresolution methods | Faiss product quantization; BitNet ternary weights | Treat compression as a tested transformation, not deletion |
| Planetary/growth motion | Capacity grows around persistent high-error regions | Net2Net, dynamic sparsity, adaptive mesh refinement | HyperAgents grows a lineage archive | Grow structured blocks only when marginal benefit per byte is high |
| Evolution | Generate, evaluate, retain, branch, and retry | Autoresearch, FunSearch, AlphaEvolve, Hyperband, PBT | HyperAgents implements editable agents and archive branching | Use a disk-backed virtual population and fixed evaluators |
| Life-like memory | Rapid episodes consolidate into slower abstractions | Complementary learning systems, replay, multi-timescale synapses | NeuroAI emphasizes modular datasets/training/benchmarks; RL-NTM uses external memory | Separate episodic, semantic, and protected slow state |
| Environment adaptation | Match computation to local resources | Model-predictive control, quantization, staged evaluation | BitNet targets low-bit inference; Matrix and Moodist show what *not* to deploy locally | Serial execution, one live candidate, measured resource envelopes |
| Rigorous proof | Claims survive formal checking and adversarial search | Theorem proving, proof kernels, counterexample generation | HyperAgents includes math-grading experiments, not proof certification | Require proof objects checked by an independent kernel |

### What genuinely survives the comparison

The cross-field pattern is:

`observe -> predict -> measure surprise -> preserve alternatives -> test ->`
`consolidate -> compress -> re-evaluate -> archive or roll back`

This is compatible with statistical physics, Bayesian inference, continual
learning, databases, control theory, evolutionary search, and the audited code.
The compatible part is the *feedback structure*, not an identity between their
physical quantities.

### What does not survive

- A scalar parameter cannot simultaneously mean truth, familiarity, physical
  mass, importance, and influence.
- Repetition is not independent confirmation.
- Negative evidence should not create “negative mass”; it changes likelihoods or
  creates a signed contradiction edge.
- Literal inverse-square attraction between weights has no established learning
  advantage.
- Quantum vocabulary does not justify amplitudes, qubits, or no-cloning rules in
  ordinary laptop software.
- Shrinking a file or lowering numeric precision is not evidence that knowledge
  survived.
- A model cannot grade its own claimed proof. The evaluator must be independent.

## 4. Mathematical specification

### 4.1 State and notation

At global event index (t), Kritjnah has:

- parameters or structured modules (	heta_t = \{\theta_i\}_{i=1}^{G});
- hypotheses (mathcal H_t = \{h_k\}_{k=1}^{K}) with probabilities (q_k);
- evidence graph (mathcal E_t) with source and dependency edges;
- fast episodic memory (M_f), semantic memory (M_s), and slow protected state
  (M_p);
- candidate archive (mathcal A_t);
- hardware state (z_t), including VRAM, RAM, device temperature, temperature
  slope, throughput, and elapsed time.

For each parameter group or concept (i), store separate values:


| Symbol | Meaning | Range or unit |
|---|---|---|
| (a_i) | current task activation | ([0,1]) |
| (c_i) | calibrated confidence in associated claims | ([0,1]) |
| (F_i) | behavioral sensitivity/Fisher importance | nonnegative |
| (m_i) | engineered structural inertia | bounded, dimensionless |
| (u_i) | update urgency | nonnegative |
| (eta_i) | effective update rate | step size |
| (H_i) | uncertainty over relevant hypotheses | nats |
| (T_c) | cognitive exploration temperature | dimensionless |
| (	au_i) | next eligible local update event | global-event index |

Parameter count, persistent bytes, transient bytes, confidence, and influence
remain different measurements.

### 4.2 Evidence dependence and Bayesian belief update

An evidence event (e) contains observation (o_e), source (s_e), a reliability
estimate (r_e), and a dependence discount (d_e). Define

$$
\rho_e = \operatorname{clip}(r_e d_e, 0, 1).
$$

If many pages repeat one original result, their shared provenance cluster lowers
(d_e); they do not count as many independent experiments. For each hypothesis,

$$
\ell_{k,t+1} = \ell_{k,t} + \rho_e \log p(o_e\mid h_k),
\qquad
q_{k,t+1}=\frac{e^{\ell_{k,t+1}}}{\sum_j e^{\ell_{j,t+1}}}.
$$

The predictive probability and surprise are

$$
p(o_e)=\sum_k q_{k,t}p(o_e\mid h_k),
\qquad
s_e=-\log(p(o_e)+\epsilon).
$$

Hypothesis entropy is

$$
H_t=-\sum_k q_{k,t}\log(q_{k,t}+\epsilon).
$$

These equations are exact only when the likelihood and dependence estimates are
valid. Calibration error must therefore be measured on held-out evidence.

### 4.3 Active energy and local clocks

“Active energy” is a compute-allocation score, not joules:

$$
E_i=\operatorname{clip}\left[
a_i(\alpha s_i+\beta H_i+\gamma D_i+\delta N_i),,0,,E_{\max}
\right],
$$

where (D_i) is committee disagreement and (N_i) is novelty. Expected progress
per unit cost determines urgency:

$$
u_i=\frac{\mathbb E[\Delta Q_i]}{\widehat C_i+\epsilon},
\qquad
\tau_i=t+\left\lceil\frac{m_i+\epsilon}{E_i+\epsilon}\right\rceil.
$$

Only groups with the smallest (	au_i) enter the serial work queue. This gives
different effective “times” while retaining a reproducible global order.

### 4.4 Structural inertia and updates

Fisher importance for group (i) can be estimated by

$$
F_i \approx \mathbb E_{(x,y)\sim R}
\left[\left\|\nabla_{\theta_i}\log p_\theta(y\mid x)\right\|_2^2\right],
$$

using a small retained probe set (R). Let (P_i) be evidence precision and
(R_i) be measured retention dependence. Then

$$
m_i=m_{\min}+\operatorname{clip}
(\lambda_P P_i+\lambda_F\widehat F_i+\lambda_R R_i,0,m_{\max}-m_{\min}),
$$

$$
\eta_i=\eta_0\frac{u_i}{m_i+\epsilon}.
$$

For a gradient-capable learner, one candidate update is

$$
\theta_i' = \theta_i-\eta_i
\left[
\nabla_{\theta_i}L_{new}
+\lambda_C F_i(\theta_i-\theta_i^*)
\right].
$$

For a local or gradient-free learner, replace the bracketed direction with a
locally measured update, a reinforcement estimator, or a candidate perturbation.
The same inertia, budget, evaluator, and rollback rules still apply.

### 4.5 Potential and exploration temperature

Define an engineered potential

$$
U(x,h;\theta)=
L_{pred}
+\lambda_v V_{constraints}
+\lambda_d L_{description}
+\lambda_p R_{provenance}
+\lambda_r L_{retention}.
$$

The free-energy-like selection objective is

$$
\mathcal F = \mathbb E_{h\sim q}[U]-T_c H(q).
$$

Higher (T_c) preserves broader alternatives; lower (T_c) concentrates on
better-supported candidates. A bounded adaptive schedule is

$$
T_c=\operatorname{clip}
(T_0+k_s S_{stagnation}+k_d\bar D-k_p\Delta Q_{recent},T_{min},T_{max}).
$$

Hardware temperature (T_h) is never used in this equation.

### 4.6 Growth and compression

Let a structured block (b) have expected quality gain (widehat{\Delta Q}_b),
persistent cost (B_b) bytes, compute cost (C_b), and interference risk (I_b):

$$
g_b=\frac{\widehat{\Delta Q}_b}
{B_b+\lambda_c C_b+\lambda_i I_b+\epsilon}.
$$

Grow only if (g_b>g_{min}), the hard budget remains satisfied, and a
function-preserving initialization is available. Compression searches for
(\phi) minimizing

$$
J_{cmp}(\phi)=L_{new}(\phi)+\lambda_{old}L_{retained}(\phi)
+\beta B(\phi)+\gamma C(\phi)+\xi D_{KL}(p_\theta\Vert p_\phi).
$$

The compact candidate is accepted only when every mandatory gate passes:

$$
\begin{aligned}
Q_{new}(\phi)&\ge Q_{new}(\theta)-\varepsilon_{new},\\
Q_j(\phi)&\ge Q_j(\theta)-\varepsilon_j &&\forall j\in\text{retained suites},\\
ECE(\phi)&\le ECE_{max},\\
B(\phi)&\le B_{target},\\
\text{provenance integrity}(\phi)&=\text{pass}.
\end{aligned}
$$

The new stage's progress score may reset to zero, but its bytes and retained
abilities do not disappear from accounting.

### 4.7 Multi-objective candidate selection

Each candidate has a vector

$$
v(a)=(Q_{new},Q_{old},-ECE,-B_{peak},-t_{wall},-E_{device},-K_{code}).
$$

Candidate (a) dominates (b) when it is no worse in every component and
strictly better in at least one. The archive stores nondominated candidates plus
a small diversity reserve. This is safer than collapsing intelligence, memory,
speed, and reliability into one scalar.

For archive parent selection, a useful starting rule from HyperAgents is

$$
\alpha_{mid}=\frac1m\sum_{j\in top_m}\alpha_j,
\quad
s_i=\sigma(\lambda(\alpha_i-\alpha_{mid})),
\quad
h_i=\frac1{1+n_i},
\quad
p_i=\frac{s_i h_i}{\sum_j s_jh_j},
$$

where (n_i) is the number of compiled children. Kritjnah should replace the
single (alpha_i) with Pareto rank and add an explicit diversity term.

### 4.8 Resource model

All memory counts:

$$
B_{total}=B_{weights}+B_{activations}+B_{optimizer}+B_{KV}+B_{replay}
+B_{indexes}+B_{archive}+B_{temporary}.
$$

The controller observes

$$
z_t=[T_h,\dot T_h,B_{VRAM},B_{RAM},\text{tokens/s},\text{faults}],
$$

and chooses a bounded action such as batch size, sequence length, recurrent steps,
offload ratio, or pause/cooldown. A short-horizon controller minimizes

$$
\sum_{k=0}^{H-1}
\left(c_Q\widehat L_{quality}+c_T\widehat T_h^2+c_M\widehat B_{peak}
+c_L\widehat t_{wall}\right)
$$

subject to immutable memory, temperature, and process limits. A firmware shutdown
temperature is a failure boundary, not an operating target. The controller needs
a verified lower soft ceiling and a safety margin; it must checkpoint and pause
before the hard boundary.

## 5. Algorithms

The pseudocode below is a specification, not executable code.

### Algorithm 1: evidence ingestion and hypothesis update

```text
INGEST(event e):
    validate schema, source identity, and content hash
    attach e to its original-source provenance cluster
    estimate reliability r and dependence discount d
    rho <- clamp(r * d, 0, 1)

    for each relevant hypothesis h_k:
        likelihood <- predictive_likelihood(e.observation | h_k)
        h_k.log_weight <- h_k.log_weight + rho * log(likelihood + epsilon)
    normalize hypothesis weights with log-sum-exp

    surprise <- -log(sum_k q_k * likelihood_k + epsilon)
    disagreement <- committee_divergence(hypotheses, e)
    append e and the update to the immutable event log
    enqueue affected concepts by expected progress per measured cost
    return surprise, disagreement
```

### Algorithm 2: serial local-clock scheduler

```text
SCHEDULE_ONE_STEP():
    for each dirty concept or parameter group i:
        active_energy <- bounded_score(
            relevance, surprise, entropy, disagreement, novelty)
        urgency <- expected_quality_gain / estimated_cost
        next_event[i] <- global_event + ceil((inertia[i] + eps) /
                                               (active_energy + eps))

    i <- minimum next_event that fits current resource envelope
    execute exactly one bounded operation for i
    record inputs, outputs, cost, seed, and state hashes
    increment global_event
```

This deliberately favors fast serial work on the laptop. At most, independent
CPU retrieval and GPU inference may overlap when measurement shows a benefit.

### Algorithm 3: pluggable learner update

```text
UPDATE_GROUP(i, batch):
    before <- locked_probe_metrics(i)
    direction <- learner_rule(i, batch)
        # one of: backprop, local derivative, policy-gradient estimate,
        # equilibrium update, or evaluated perturbation
    step <- base_rate * urgency[i] / (inertia[i] + eps)
    candidate <- apply(theta[i], direction, step)

    if finite(candidate) and local_constraints_pass(candidate):
        install candidate in a temporary state
        after <- locked_probe_metrics(i)
        if retention_and_quality_gates_pass(before, after): accept
        else: rollback
    else:
        rollback
    log the result, including failures
```

The first experiment compares update rules at matched bytes, examples, wall time,
and device energy. No method wins by definition.

### Algorithm 4: diversity-aware consolidation

```text
CONSOLIDATE():
    candidates <- sample episodic memory using a mixture of:
        uniform reserve
        high surprise
        high uncertainty or contradiction
        rare skill/source cluster
        high retention importance
        old items near forgetting threshold

    deduplicate by provenance and semantic near-duplicate index
    replay candidates through the learner
    estimate behavioral importance and calibration
    transfer stable abstractions fast -> semantic -> protected state
    retain counterexamples and minority capabilities explicitly
    write a reversible consolidation checkpoint
```

### Algorithm 5: developmental grow--compress cycle

```text
DEVELOP(stage):
    freeze stage evaluator and resource envelope
    baseline <- evaluate(current_model, all locked suites)

    while promotion criteria are not met:
        residuals <- find high-error, high-value regions
        proposal <- choose one structured growth or learning intervention
        if proposal fits hard budget and predicted gain-per-byte is sufficient:
            create function-preserving candidate when possible
            train candidate for one resource rung
            evaluate current skill + all retained skills
            archive if nondominated; otherwise discard
        consolidate on a fixed schedule

    compact <- distill/prune/quantize a copy under J_cmp
    if every retention, calibration, memory, and recovery gate passes:
        promote compact as next baseline and reset only the stage progress score
    else:
        keep the pre-compression baseline and record the failed attempt
```

### Algorithm 6: bounded self-research harness

```text
RESEARCH_FOREVER_UNTIL_EXTERNALLY_STOPPED():
    require owner-enabled later phase
    keep evaluator, sandbox, limits, and supervisor outside editable scope
    archive <- {evaluated baseline}

    loop:
        telemetry <- read resource controller
        if unsafe or no valid checkpoint:
            restore valid checkpoint; cool down; continue

        parent <- sample Pareto archive by quality, diversity, and child count
        idea <- propose one falsifiable modification from failures and literature
        patch <- generate change only inside the declared editable surface

        if static checks or isolation checks fail:
            archive failure; continue

        run cheap rung with time, memory, network, and filesystem limits
        if cheap rung fails: archive failure; continue
        run progressively larger rungs only while gates pass

        report <- evaluate on locked train/validation/retention/adversarial suites
        if report is nondominated and reproducible:
            add content-addressed candidate and report to archive
        else:
            discard candidate but retain its experiment record
```

This borrows Autoresearch's narrow editable surface and fixed trials, HyperAgents'
lineage archive, Hyperband's rungs, and BOxCrete's uncertainty-aware experiment
selection. It rejects self-certification and unbounded individual runs.

### Algorithm 7: experiment selection by expected information gain

```text
CHOOSE_EXPERIMENT(possible_experiments):
    for each experiment x:
        eig[x] <- H(current hypotheses)
                  - expected_outcome_entropy_after(x)
        score[x] <- eig[x] * source_reliability[x] * novelty[x]
                    / (time[x] + byte_cost[x] + device_energy[x] + eps)
    return feasible x with maximum score,
           with a reserved probability for diverse exploration
```

### Algorithm 8: checkpoint, thermal control, and recovery

```text
SUPERVISE():
    every control interval:
        read temperature, temperature slope, VRAM, RAM, throughput, process health
        predict the next horizon for each feasible action
        choose the highest-throughput action satisfying every hard constraint

        if predicted soft ceiling will be crossed:
            reduce batch/context/recurrent steps, checkpoint, or pause
        if process crashes or heartbeat expires:
            terminate only the failed child process
            validate last checkpoint and event-log checksum
            resume from the last legitimate state with a smaller envelope
        always honor the external stop signal
```

### Algorithm 9: rigorous mathematics research loop

```text
FORMAL_RESEARCH(conjecture):
    import only versioned definitions and already verified lemmas
    decompose the conjecture into typed, machine-checkable subgoals

    loop until externally stopped or a complete proof object is verified:
        choose a subgoal by expected proof progress per compute cost
        retrieve original sources and exact dependencies
        generate candidate lemmas, proof terms, or counterexamples
        run symbolic checks, numerical falsification, and the proof kernel

        if a proof term verifies:
            add it to the dependency graph and recheck affected descendants
        else:
            retain the counterexample or failure trace; do not promote the claim

        periodically rebuild the complete proof from a clean environment
```

For the Riemann hypothesis, numerical verification of zeros, persuasive prose,
agreement among agents, or a high reward is not a proof. Stopping on “proof found”
requires an independently checkable formal object whose assumptions and imported
lemmas are explicit. External mathematical review remains necessary.

## 6. System architecture

```text
                         IMMUTABLE / OWNER CONTROLLED
  +-----------------------------------------------------------------------+
  | stop control | resource limits | evaluator | proof kernel | audit log |
  +-------------------------------+---------------------------------------+
                                  |
                         signed evaluation report
                                  v
  +------------------------- research supervisor -------------------------+
  | candidate generator -> isolated executor -> Pareto archive -> rollback |
  +-------------------------------+---------------------------------------+
                                  |
                         approved model candidate
                                  v
  +------------------------- developmental learner -----------------------+
  | hypothesis pool | sparse recurrent core | local-clock scheduler        |
  | fast episodes   | semantic memory       | protected slow state         |
  | provenance graph| retrieval index       | grow/compress controller     |
  +-------------------------------+---------------------------------------+
                                  |
                            bounded tool calls
                                  v
  +---------------------------- tools ------------------------------------+
  | read-only research retrieval | calculator | code runner | proof checker|
  +-----------------------------------------------------------------------+
```

### Required records

`EvidenceEvent`

```text
id, content_hash, observation, source_uri, source_author,
retrieved_at, source_cluster, reliability, dependence_discount,
supports[], contradicts[], derivation, evaluator_version
```

`Hypothesis`

```text
id, statement, log_weight, likelihood_model, assumptions[],
supporting_events[], counterevents[], predictions[], status
```

`ConceptGroup`

```text
id, parameter_refs[], activation, confidence, fisher_importance,
inertia, urgency, uncertainty, next_event, timescale_channels[]
```

`Candidate`

```text
id, parent_ids[], code_hash, model_hash, data_hash, seed,
editable_surface, resource_rung, metrics_vector, failures[], status
```

`EvaluationReport`

```text
candidate_id, evaluator_hash, per_skill_metrics, retention_deltas,
calibration, peak_vram, peak_ram, wall_time, energy_if_available,
temperature_trace, proof_kernel_result, reproducibility_result
```

### Trust boundary

The editable candidate may change learner code, update rules, architecture blocks,
prompts, or schedules only when the experiment declares them in scope. It may not
change:

- evaluation data or scoring code;
- proof-kernel binaries or accepted axioms;
- resource limits, stop handling, or supervisor heartbeat;
- credential stores, identity, network allowlists, or publication controls;
- historical logs or previously evaluated artifacts.

## 7. Device-specific plan

The inspected device is an HP Pavilion Gaming Laptop 15-dk1xxx with an
8-core/16-thread Intel Core i7-10870H, about 32 GB RAM, and a GeForce GTX 1650 Ti
with 4 GB VRAM. That changes the design materially:

- Keep only one trainable candidate in VRAM. Store the population as compressed,
  content-addressed checkpoints on disk.
- Favor a compact learner, short contexts, gradient accumulation, activation
  checkpointing only when it actually lowers peak memory, and CPU-backed retrieval.
- Quantized inference can help, but native low-bit training and post-training
  quantization are different. BitNet's strongest results use models trained for
  ternary weights; they do not prove that an arbitrary existing model can be made
  equivalent by rounding it.
- Use structured sparsity or whole modules. Arbitrary scalar sparsity often saves
  theoretical operations without making this GPU's dense kernels faster.
- Do not run a live multi-agent population, distributed Ray stack, or RDMA stack.
  Time-multiplex candidates and keep orchestration in a lightweight local process.
- Schedule CPU indexing, source parsing, and proof checking separately from GPU
  inference; overlap only after profiling shows lower total time and safe memory.
- Measure tokens/second, peak VRAM, peak RAM, task score, and temperature for every
  rung. Optimize observed end-to-end work, not advertised parameter counts.
- The owner-reported 82 degrees Celsius shutdown point must be treated as an
  unverified emergency boundary, not as usable headroom. Establish a lower soft
  ceiling from telemetry and retain a margin for sensor lag and workload spikes.

The realistic target is a capable small local research assistant plus strong
retrieval, tools, memory, verification, and iterative search. “Frontier-level
intelligence” is not a property that a 4 GB GPU or a persistence prompt can
guarantee. The harness can improve reliability and task completion without
pretending it changed the underlying model's fundamental capacity.

## 8. Audit of all public starred repositories

### 8.1 `microsoft/BitNet` — use for efficient inference research

**Inspected:** README, repository structure, BitNet b1.58 paper, 2B4T technical
report, and bitnet.cpp paper.
**Algorithm:** replace dense linear weights by ternary values. For an underlying
matrix (W\in\mathbb R^{n\times m}), the paper uses

$$
\gamma=\frac{1}{nm}\sum_{ij}|W_{ij}|,
\qquad
\widetilde W=\operatorname{RoundClip}(W/(\gamma+\epsilon),-1,1).
$$

Activations are quantized per token. Specialized kernels replace much of dense
floating-point multiplication with low-bit operations.
**Use:** investigate a native compact core or efficient inference backend.
**Do not infer:** ternary weights create intelligence, or arbitrary quantization
preserves every capability.
**License:** MIT.

### 8.2 `facebookresearch/HyperAgents` — use the archive, not unrestricted mutation

**Inspected:** README, paper, `generate_loop.py`, `meta_agent.py`, `task_agent.py`,
parent-selection code, evaluation paths, and safety discussion.
**Algorithm:** select an archived parent, let its integrated task/meta agent propose
a modified child, evaluate the child, and retain valid variants. The paper's main
selection rule balances a sigmoid of performance with (1/(1+n_i)) child-count
novelty. It reports task and meta-level improvements, while also reporting that a
self-modified parent selector did not beat the handcrafted selector.
**Use:** lineage archive, staged evaluation, transfer analysis, and metacognitive
experiments in an isolated later phase.
**Do not copy directly:** the current code executes generated changes in containers
and warns that they can be destructive. On this laptop it is also too heavy and
depends on remote services. The evaluator and safety boundary must remain fixed.
**License:** CC BY-NC-SA 4.0; concepts may be cited, but code cannot simply be
absorbed into an unrestricted public project without respecting its terms.

### 8.3 `facebookresearch/matrix` — borrow message contracts, not the cluster

**Inspected:** README, peer-to-peer agent documentation, paper, configuration
layout, orchestrator, resource-client, actor, metrics, and sandbox paths.
**Algorithm:** represent control and data flow as serializable messages in
distributed queues; schedule rows independently; offload expensive inference and
containers to services; exploit data, task, and agent parallelism. The paper
reports higher throughput in distributed settings under matched hardware.
**Use:** explicit message schemas, row-level resumability, instrumentation, and
separation of agents from resources.
**Do not deploy initially:** Ray actors, distributed inference services, and three
parallelism axes add overhead and exceed the single-laptop need. Use one serial
queue with durable messages.
**License:** MIT.

### 8.4 `facebookresearch/SustainableConcrete` — use Bayesian experiment selection

**Inspected:** README, BOxCrete papers, model/package layout, tutorials, calibration,
and multi-objective optimization design.
**Algorithm:** a Gaussian process places a posterior over an expensive response.
For training inputs (X), observations (y), kernel (K), and noise variance
(\sigma_n^2), a standard GP posterior at (x_*) is

$$
\mu_*=k_*^T(K+\sigma_n^2I)^{-1}y,
$$

$$
\sigma_*^2=k(x_*,x_*)-k_*^T(K+\sigma_n^2I)^{-1}k_*.
$$

An acquisition function selects the next costly experiment by predicted reward
and uncertainty; Pareto analysis balances several outcomes.
**Use:** choose architecture, curriculum, and compression experiments by expected
information or hypervolume gain rather than brute force.
**Caveat:** reported concrete-prediction accuracy is evidence for that materials
domain, not for general learner improvement.
**License:** MIT.

### 8.5 `facebookresearch/moodist` — exclude from the local prototype

**Inspected:** README, requirements, collective/queue/TCP-store documentation, and
repository layout.
**Algorithm:** a PyTorch process group provides CPU/CUDA collectives and queues over
RDMA-capable networking.
**Use:** only as a future reference for cluster collectives and distributed queues.

**Why excluded:** it requires Linux, recent CUDA/PyTorch, and supported RDMA hardware
such as InfiniBand or EFA. The inspected laptop does not have that environment.
**License:** MIT.

### 8.6 `facebookresearch/neuroai` — use its modular research discipline

**Inspected:** README, package boundaries, documentation links, benchmark/training/
data roles, execution-cache dependency, and NeuralSet paper link.
**Algorithmic contribution:** this is a suite rather than one learning rule:
NeuralSet loads data, NeuralFetch obtains curated datasets, NeuralTrain runs
training, and NeuralBench evaluates models.
**Use:** separate data acquisition, loading, training, caching, and benchmarking;
build reproducible dataset adapters rather than one monolith.
**Do not infer:** neuroscience datasets make an architecture brain-like or solve
continual learning.
**License:** MIT, with separate terms for third-party content.

### 8.7 `facebookresearch/three_bricks` — use statistical audit ideas

**Inspected:** README, paper, generation/evaluation entry points, scoring modes,
attacks, and license.
**Algorithm:** generation leaves a keyed statistical signal in token choices;
detection aggregates context-conditioned scores and computes a z-test,
Neyman--Pearson statistic, or p-value. Unique-context scoring reduces invalid
double-counting.
**Use:** the transferable lesson is rigorous false-positive control, deduplication,
and provenance tests. A claim should cross a predeclared significance threshold,
not merely “look convincing.”
**Not core cognition:** watermarking does not improve reasoning or learning.
**License:** CC BY-NC 4.0.

### 8.8 `ilyasu123/rlntm` — use the discrete-interface lesson, not the codebase

**Inspected:** complete README, repository tree, reinforcement modules,
`efficient_rlntm.lua`, task scripts, logs, and original RL-NTM paper.
**Algorithm:** a recurrent controller samples discrete input-head, memory-head, and
output-head actions. REINFORCE estimates a policy gradient with a learned baseline:

$$
\nabla_\theta J\approx
\sum_t (R-b_t)\nabla_\theta\log\pi_\theta(a_t\mid s_t),
$$

with entropy incentives used to preserve exploration. External tapes make
algorithmic behavior possible, but training is fragile; the README reports only
30--50% successful seeds for its experiments and very long CPU runs.
**Use:** treat memory, search, databases, and proof checkers as explicit discrete
interfaces; log execution traces.
**Why not reuse directly:** old Lua/Torch code, incomplete experimental file, high
variance, noncommercial license, and no demonstrated modern general reasoning.
**License:** CC BY-NC 4.0.

### 8.9 `facebookresearch/theseus` — use for differentiable constraints

**Inspected:** README, paper, optimizer list, backward modes, example objective,
and package layout. The starred `ahojnnes/theseus` fork is the same upstream
lineage and is recorded separately below.
**Algorithm:** for residuals (r_j(x)), nonlinear least squares minimizes

$$
\frac12\sum_j\|r_j(x)\|^2.
$$

Gauss--Newton solves

$$
(J^TJ)\Delta=-J^Tr,
$$

while Levenberg--Marquardt uses

$$
(J^TJ+\lambda I)\Delta=-J^Tr.
$$

Differentiating through or implicitly around the optimizer allows expert
constraints and learned components in one end-to-end objective.
**Use:** constraint-satisfaction layers, energy minimization, and small structured
optimization problems.
**Caveat:** this is a gradient-compatible tool, not evidence that the whole learner
should use backpropagation. Some GPU paths need a CUDA toolkit and sparse solvers.
**License:** MIT.

### 8.10 `ahojnnes/theseus` — duplicate fork, not independent evidence

**Inspected:** repository metadata, README, and upstream relation.
**Finding:** GitHub identifies it as a fork of `facebookresearch/theseus`.
**Use:** no separate algorithmic contribution was identified in the audited public
metadata. Track it only if a fork-specific commit later becomes relevant.
**License:** MIT.

### 8.11 `ahojnnes/faiss` — use upstream Faiss for retrieval

**Inspected:** fork metadata, upstream README, algorithm overview, index tradeoffs,
and paper links. GitHub identifies the starred repository as a fork of
`facebookresearch/faiss`.
**Algorithms:** exact L2 or inner-product search; inverted files narrow the search
to selected clusters; product quantization splits (x) into sub-vectors and stores
codebook indices,

$$
x\approx[q_1(x_1),\ldots,q_M(x_M)],
$$

reducing memory at the cost of recall. Graph indexes such as HNSW trade added graph
memory for fast approximate search.
**Use:** CPU semantic retrieval, near-duplicate detection, curriculum diversity,
and provenance lookup. Start with exact search at small scale and benchmark recall
before compression.
**Not a learner:** retrieval expands accessible information but does not alter the
core model's weights or certify truth.
**License:** MIT.

### 8.12 `bcherny/bst-next` — use as a curriculum-quality example

**Inspected:** all three implementations, tests, package metadata, and license.
**Algorithms:** the in-order successor of a node is the minimum of its right subtree
if one exists; otherwise it is the first ancestor greater than the node. One version
stores parent pointers, one searches from the root, and one materializes the full
in-order traversal. Their time/space tradeoffs differ:

- parent-pointer version: (O(h)) time and (O(1)) auxiliary space;
- root-search version: (O(h)) to recover ancestry, subject to implementation;
- materialized traversal: (O(n)) time and (O(n)) list space.

**Use:** compact lessons where equivalent behavior is implemented with different
state, time, and elegance tradeoffs—ideal for testing abstraction and cost-aware
algorithm selection.
**Caveat:** the elegant version indexes the successor without guarding the final
node, so its stated interface needs an edge-case test before reuse.
**License:** BSD-3-Clause.

### 8.13 `bcherny/js-math` — use as a tiny parser lesson, not a dependency

**Inspected:** the complete `index.js` and `test.js`; there is no README or declared
license in the public metadata.
**Algorithm:** tokenize characters, lex numbers/operators, recursively parse prefix
expressions into nested arrays, then recursively evaluate the tree.
**Finding:** the parser's recursive handling of nested parentheses has an explicit
failing/TODO case in the tests, and evaluation tests are commented out.
**Use:** a minimal curriculum task for parsing, compositional execution, test-driven
repair, and failure-trace learning.
**Do not copy:** no license is declared; use the idea or write an independent test
fixture.
**License:** not declared.

## 9. Cross-repository synthesis

| Layer | Best source ideas | Kritjnah adaptation |
|---|---|---|
| Efficient core | BitNet | Benchmark native low-bit or other compact cores; never assume rounding preserves ability |
| Self-research | Autoresearch + HyperAgents | One editable surface, bounded rungs, lineage/Pareto archive, immutable evaluator |
| Experiment choice | SustainableConcrete + Hyperband | Posterior uncertainty and expected gain per byte/second; stop weak trials early |
| Orchestration | Matrix | Durable serial messages and resumable rows without cluster dependencies |
| External memory | RL-NTM + Faiss + LSM principles | Explicit tool interfaces, exact-first retrieval, episodic-to-semantic compaction |
| Constraints | Theseus | Differentiable or solver-backed potential terms where useful |
| Audit | Three Bricks + truth maintenance | Predeclared statistical thresholds, dependence-aware provenance, counterevidence |
| Research discipline | NeuroAI | Separate datasets, loaders, trainers, benchmarks, and caches |
| Curriculum | bst-next + js-math | Small tasks with multiple algorithms, edge cases, and measurable resource tradeoffs |
| Distributed future | Moodist | Defer until supported cluster hardware exists |

The most important negative result is architectural: installing all these projects
would not create a smarter system. It would create a large, conflicting dependency
stack. Kritjnah should reimplement only small, license-compatible interfaces and
algorithms after each earns its place in an ablation.

## 10. Evaluation plan

### Phase 0: measurement harness

Implement no self-modification. Establish deterministic seeds, event logging,
content-addressed checkpoints, task suites, memory accounting, temperature
telemetry, crash recovery, and a fixed evaluator.

**Pass:** a killed experiment resumes from the last valid checkpoint; repeated
evaluation agrees within a declared tolerance; all resource figures are recorded.

### Phase 1: knowledge formation

Use small arithmetic, parsing, sequence, and contradictory-evidence tasks. Compare:

1. single hypothesis versus a small hypothesis pool;
2. raw repetition versus dependence-discounted evidence;
3. uniform updates versus evidence/Fisher inertia;
4. no replay versus diversity-aware fast/slow replay.

**Pass:** better held-out calibration or retention at matched total bytes and time.

### Phase 2: growth and compression

Compare a fixed-capacity baseline with function-preserving structured growth,
followed by distillation, structured pruning, or low-bit conversion.

**Pass:** the compact candidate meets every per-skill retention tolerance and uses
fewer measured persistent bytes or less measured latency. Average score alone is
insufficient.

### Phase 3: research-loop simulation

Run the archive/search harness on a deliberately small editable component. Compare
greedy keep/revert, random archive selection, performance/child-count selection,
and Bayesian experiment selection.

**Pass:** more reproducible Pareto improvements per device-hour than the simplest
baseline, without evaluator changes or resource-limit violations.

### Phase 4: formally checked mathematics curriculum

Begin with already solved, machine-checkable theorem sets. Measure proof-check
success, false-claim rate, dependency correctness, counterexample discovery, and
generalization to held-out lemmas.

**Pass:** verified proof objects on held-out tasks with zero accepted invalid proof
objects. Only after this phase should open conjectures be used as research targets.

### Required ablations

- remove provenance dependence correction;
- remove hypothesis diversity;
- remove Fisher/evidence inertia separately;
- remove uniform replay reserve;
- replace local clocks with synchronous updates;
- replace Pareto selection with a scalar score;
- disable growth, then disable compression;
- compare gradients, local updates, reinforcement estimators, and perturbation
  search under equal resources;
- compare exact retrieval with compressed retrieval at measured recall;
- compare serial execution with any proposed overlap using end-to-end throughput.

### Automatic rejection conditions

Reject a candidate if it modifies the evaluator, loses a mandatory earlier skill
beyond tolerance, produces an invalid proof object, cannot reproduce its gain,
exceeds a hard resource limit, corrupts provenance, depends on undeclared external
state, or cannot be rolled back cleanly.

## 11. Failure modes and controls

| Failure | Detection | Control |
|---|---|---|
| Reward hacking | score rises while locked adversarial suites regress | immutable multi-suite evaluator; audit traces |
| Catastrophic forgetting | per-skill retention delta | replay, inertia, rollback |
| Archive collapse | low behavioral/structural diversity | novelty reserve and lineage-aware sampling |
| Noisy evidence capture | poor calibration; duplicated provenance clusters | source dependence discount and reliability models |
| Endless repeated failure | identical change/failure hashes | tabu cache, novelty requirement, smaller fallback rung |
| False proof | proof kernel reject or counterexample | never promote prose; retain failure trace |
| Compression damage | skill/calibration/provenance gates | revert compact candidate |
| Thermal oscillation | repeated crossings and steep (\dot T_h) | predictive margin, hysteresis, checkpoint/cooldown |
| Disk growth | archive bytes exceed quota | retain metrics/logs; deduplicate blobs; policy-controlled eviction |
| Unsafe self-edit | diff escapes editable surface | reject before execution; isolated child process |
| Dependency/license conflict | software-bill-of-materials check | reimplement small interfaces; preserve attribution and terms |

## 12. Decisions and open questions

### Recommended decisions

1. Use the physics ideas only as precisely named control variables.
2. Build the fixed evaluator and event log before the learner.
3. Start with a small recurrent core and external memory, not a giant monolith.
4. Permit backpropagation as one baseline; require alternatives to beat it under
   matched resources.
5. Use serial experiments and a disk-backed virtual population.
6. Adopt Pareto retention rather than a single intelligence score.
7. Keep formal verification and all safety/resource controls outside editable code.
8. Treat the Riemann hypothesis as a distant benchmark, not a training signal.

### Open research questions

- What local or hybrid update rule gives the best retention per device-hour?
- How should source dependence and reliability be calibrated without circularity?
- What concept-group granularity makes structural inertia useful and affordable?
- Which function-preserving growth operations work for the selected compact core?
- Can compression preserve uncertainty and rare capabilities, not just mean output?
- Does a multi-hypothesis pool improve real reasoning enough to justify its bytes?
- Can expected information gain be estimated cheaply enough to beat simple queues?
- Which formal theorem corpus supplies a fair developmental curriculum?

## 13. Primary and official sources

### Physics, information, and learning

- Shannon, *A Mathematical Theory of Communication* (1948):
  https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
- Jaynes, *Information Theory and Statistical Mechanics* (1957):
  https://journals.aps.org/pr/abstract/10.1103/PhysRev.106.620
- Landauer, *Irreversibility and Heat Generation in the Computing Process* (1961):
  https://www.cpt.univ-mrs.fr/~verga/pdfs/Landauer-1961uq.pdf
- Bennett, *Logical Reversibility of Computation* (1973):
  https://www.cs.princeton.edu/courses/archive/fall06/cos576/papers/bennett73.html
- Reeb and Wolf, finite-size Landauer equality (2014):
  https://arxiv.org/abs/1306.4352
- Einstein, general relativity (1916):
  https://sites.pitt.edu/~jdnorton/teaching/Einstein_graduate/pdfs/Einstein_GR_1916.pdf
- Noether, invariant variational problems (1918 translation):
  https://arxiv.org/abs/physics/0503066
- Bekenstein, black-hole entropy (1973):
  https://journals.aps.org/prd/abstract/10.1103/PhysRevD.7.2333
- Jacobson, thermodynamics of spacetime (1995):
  https://arxiv.org/abs/gr-qc/9504004
- Wootters and Zurek, no-cloning (1982):
  https://doi.org/10.1038/299802a0
- Ollivier, Poulin, and Zurek, environment as witness (2004):
  https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.93.220401
- Page and Wootters, relational time (1983):
  https://journals.aps.org/prd/abstract/10.1103/PhysRevD.27.2885
- Connes and Rovelli, thermal time (1994):
  https://arxiv.org/abs/gr-qc/9406019
- Kadanoff, scaling and coarse-graining (1966):
  https://journals.aps.org/ppf/abstract/10.1103/PhysicsPhysiqueFizika.2.263
- Tishby, Pereira, and Bialek, information bottleneck:
  https://arxiv.org/abs/physics/0004057
- Rissanen, minimum description length (1978):
  https://research.ibm.com/publications/modeling-by-shortest-data-description
- Hopfield, neural networks and physical systems (1982):
  https://pubmed.ncbi.nlm.nih.gov/6953413/
- Rao and Ballard, predictive coding (1999):
  https://www.nature.com/articles/nn0199_79
- Kirkpatrick et al., elastic weight consolidation (2017):
  https://doi.org/10.1073/pnas.1611835114
- Benna and Fusi, multi-timescale memory (2016):
  https://pubmed.ncbi.nlm.nih.gov/27694992/
- McClelland, McNaughton, and O'Reilly, complementary learning systems (1995):
  https://web.stanford.edu/~jlmcc/papers/McCMcNaughtonOReilly95.pdf

### Search, learning, control, and self-research

- Karpathy, Autoresearch repository and protocol:
  https://github.com/karpathy/autoresearch
- HyperAgents paper and repository:
  https://arxiv.org/abs/2603.19461 and
  https://github.com/facebookresearch/HyperAgents
- AlphaEvolve:
  https://arxiv.org/abs/2506.13131
- FunSearch official implementation:
  https://github.com/google-deepmind/funsearch
- Hyperband:
  https://www.jmlr.org/beta/papers/v18/16-558.html
- Population-based training:
  https://arxiv.org/abs/1711.09846
- Query by committee and active learning:
  https://www.jmlr.org/papers/volume5/baram04a/baram04a.pdf
- Doyle, truth-maintenance systems:
  https://www.sciencedirect.com/science/article/pii/0004370279900080
- Provenance-aware storage:
  https://static.usenix.org/events/usenix06/tech/full_papers/muniswamy-reddy/muniswamy-reddy_html/index.html
- EWC/SI/MAS analysis:
  https://arxiv.org/abs/2006.06357
- Adaptive computation time:
  https://arxiv.org/abs/1603.08983
- Prioritized replay analysis:
  https://proceedings.mlr.press/v180/pan22a/pan22a.pdf
- Natural gradient:
  https://arxiv.org/abs/1808.07172
- Net2Net:
  https://arxiv.org/abs/1511.05641
- RigL:
  https://arxiv.org/abs/1911.11134
- Asynchronous coordinate updates:
  https://proceedings.mlr.press/v202/wu23n.html
- LSM-tree compaction design space:
  https://arxiv.org/abs/2202.04522
- Model predictive control:
  https://web.stanford.edu/~boyd/papers/code_gen_rhc.html
- Dijkstra, self-stabilization:
  https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD426.html

### Audited starred repositories and their papers

- BitNet: https://github.com/microsoft/BitNet
- BitNet b1.58: https://arxiv.org/abs/2402.17764
- bitnet.cpp: https://arxiv.org/abs/2502.11880
- Matrix: https://github.com/facebookresearch/matrix and
  https://arxiv.org/abs/2511.21686
- SustainableConcrete / BOxCrete:
  https://github.com/facebookresearch/SustainableConcrete and
  https://arxiv.org/abs/2603.21525
- Moodist: https://github.com/facebookresearch/moodist
- NeuroAI: https://github.com/facebookresearch/neuroai
- Three Bricks: https://github.com/facebookresearch/three_bricks and
  https://arxiv.org/abs/2308.00113
- RL-NTM: https://github.com/ilyasu123/rlntm and
  https://arxiv.org/abs/1505.00521
- Theseus: https://github.com/facebookresearch/theseus and
  https://arxiv.org/abs/2207.09442
- Starred Theseus fork: https://github.com/ahojnnes/theseus
- Starred Faiss fork: https://github.com/ahojnnes/faiss
- Faiss upstream: https://github.com/facebookresearch/faiss and
  https://arxiv.org/abs/2401.08281
- BST successor examples: https://github.com/bcherny/bst-next
- Prefix-math parser: https://github.com/bcherny/js-math

## 14. Final blueprint in one sentence

Kritjnah should be a compact, provenance-aware, multi-timescale learner inside a
bounded evolutionary research harness that allocates serial compute by uncertainty,
grows only where measured residual error justifies the bytes, compresses only when
every retained capability survives, adapts to the device through an independent
controller, and accepts mathematical claims only as externally verified proof
objects.
