# Kavi's current pathway model: mathematics and algorithms

Author: Arnav123-s. Specification checked against `kavi/wave_core.py`,
`kavi/pathway_trials.py`, and `kavi/strategy_trials.py` on 2026-09-04.

## 1. What the model actually is

The active text-model family is a **classical, complex-valued, sparse recurrent
neural network with learned, activity-dependent routing**. Complex numbers are
implemented as pairs of real numbers. It uses gradient descent through time via
Adam. It is not a quantum computer, a shortest-path solver, a mixture of
independent expert models, or the earlier symbolic circuit in this repository.

Child-friendly version: a letter enters a small network of adjustable channels.
Each channel can weaken, rotate, mix, or keep some signal. The resulting state
helps predict the next letter. A teacher's correction changes the adjustments.
The same network is reused on the next question; it does not save the question
as a retrievable transcript inside its weights.

There is an important gap between the proposed idea and this implementation:
**the paths are not its only learned memory**. Input encodings and output
decoding weights also learn. For the tested 64-node circuit, those two matrices
hold 65,536 of 66,880 parameters, about 98%. Parameter count is not a measurement
of which part supplies the intelligence, but it prevents a claim that all
learning has already been moved into the routes.

## 2. State, parameters, and time

An input is UTF-8 bytes, not pictures of letters:

$$x_t\in\{0,\ldots,255\},\qquad s_t\in\mathbb C^N.$$

Here $N=64$, $K=4$ incoming route slots per node, and $H=2$ mixing hops per
byte. One symbol may contain several bytes. The model's time index counts byte
updates; it is not physical time, relativity, or a subjective clock.

| Symbol | Code parameter | Meaning |
| --- | --- | --- |
| $E\in\mathbb R^{256\times2N}$ | `embedding.weight` | Learned byte encoding. |
| $S_{ir}$ | `sources` buffer | Source node for incoming slot $r$ of node $i$. |
| $a_{ir}$ | `edge_logits` | Base routing preference. |
| $v_{ir}$ | `activity_gain` | How source magnitude changes routing preference. |
| $g_{ir}$ | `conductance` | Transmission-strength parameter. |
| $\phi_{ir}$ | `phase` | Rotation angle in the two-dimensional signal plane. |
| $\mu_i$ | `memory_gate` | Blend between previous state and current byte. |
| $W\in\mathbb R^{256\times2N},b\in\mathbb R^{256}$ | `readout` | Next-byte prediction. |

Initially $S_{ir}=(i+d_r)\bmod N$ for offsets $d=(0,1,3,7)$. These are
destination-indexed incoming sources, not evidence of discovered conceptual
regions. Ordinary learning changes continuous parameters but not $S$.

Persistent parameters and graph indices are learned/model state. The transient
state $s_t$ summarizes the current question and is reset between independent
questions. Optimizer moments are additional training state. All occupy memory.

## 3. Exact forward equations

Let $e_t=\operatorname{complex}(E[x_t])$ and $\alpha_i=\sigma(\mu_i)$.
First blend the old state and input:

$$z_i^{(0)}=\alpha_i s_{t-1,i}+(1-\alpha_i)e_{t,i}.$$

For each hop $h=0,\ldots,H-1$, calculate source magnitudes and routing:

$$u_{ir}=z_{S_{ir}}^{(h)},\qquad
q_{ir}=a_{ir}+\tanh(v_{ir})|u_{ir}|,$$

$$\pi_{ir}=\frac{\exp(q_{ir})}{\sum_{r'=1}^{K}\exp(q_{ir'})},
\qquad c_{ir}=\pi_{ir}\sigma(g_{ir}),$$

$$m_i=\sum_{r=1}^{K}c_{ir}e^{\mathrm{i}\phi_{ir}}u_{ir},$$

$$\widetilde z_i=z_i^{(h)}+\tfrac12m_i+\tfrac14e_{t,i},
\qquad
z_i^{(h+1)}=\frac{\widetilde z_i}{\sqrt{1+|\widetilde z_i|^2}}.$$

Set $s_t=z^{(H)}$. Flatten its real/imaginary coordinates to $\bar s_t$:

$$\ell_t=W\bar s_t+b,\qquad
p_\theta(x_{t+1}=j\mid x_{1:t})=\operatorname{softmax}(\ell_t)_j.$$

Inference chooses $\arg\max_j\ell_{t,j}$, feeds that byte back through the
same circuit, and repeats until newline or the output limit. Equal prompts and
weights give deterministic output here; repeated answers alone do not establish
learning, and repeated success on the same prompt is not fresh evidence.

### What the wave mathematics does and does not imply

For two contributions $A$ and $B$:

$$|A+B|^2=|A|^2+|B|^2+2\operatorname{Re}(A\overline B).$$

The final term can reinforce or cancel signal. This is ordinary classical
wave-like interference, calculated with real multiplications and additions.
The full recurrence is nonlinear and not unitary; its norm is not conserved.
It implements neither entangled quantum states nor a quantum speedup. Routing
is a soft mixture of available links, not a proof that the optimal path wins.
All allocated route slots are evaluated; weak softmax gates are not hard skips.

Normalization gives the exact finite-input property

$$|z_i^{(h+1)}|^2=\frac{|\widetilde z_i|^2}{1+|\widetilde z_i|^2}<1.$$

It bounds activation magnitudes, not training error, correctness, accumulated
rounding error, or the gradients of the complete recurrence.

## 4. How a correction becomes a parameter update

For example $b$, the teacher supplies a question prefix $p_b$ and verified
answer $y_b$ followed by newline. Training feeds the combined sequence, but
scores **only answer bytes**. Let $T_b$ index those target bytes:

$$L_b(\theta)=-\frac1{|T_b|}\sum_{t\in T_b}
\log p_\theta(y_{b,t}\mid p_b,y_{b,<t}),\qquad
L(\theta)=\frac1B\sum_{b=1}^{B}L_b(\theta).$$

The answer-byte average prevents longer answers from automatically receiving
more weight than short answers. Question bytes condition the prediction and
receive gradients through the recurrence; they are not the scored targets.
Evaluation, unlike teacher-forced training, generates without the answer.
For these trials $B=4$ and each combined example is at most 256 UTF-8 bytes.

Backpropagation calculates $d=\nabla_\theta L$ and clips its global norm to
at most one. Adam uses moving averages of this gradient and its square, with
the checkpoint's optimizer state and learning rate 0.003. This changes $E,W,b,
\mu,a,v,g,\phi$: not only the paths. Generated mistakes are never silently
reused as correct targets. In these symbol trials the explanatory sentence
attached to an exercise is **not** itself a training target.

```text
TEACH_ONE_UPDATE(verified examples, parallel width w):
    clear accumulated parameter gradients
    split four independent examples into chunks of w rows
    for each chunk:
        reset each row's sequence state
        run the same circuit through prefix and verified answer
        sum each row's mean answer loss, divided by FOUR
        backpropagate and accumulate gradients
    clip the combined gradient; perform ONE Adam update
    if testing route damping: keep only 25% of route displacement
```

For independent rows,

$$\nabla L=\frac14\sum_{b=1}^4\nabla L_b.$$

Thus 4 rows together, 2+2 rows, or 1+1+1+1 rows represent the same objective
and one update, up to floating-point rounding. Updating Adam separately after
each row would not be equivalent. Batch parallelism does not make a single
question branch into four minds; bytes still pass through recurrent time in
order. Only independent rows and the calculations inside a hop can run together.

## 5. What could explain the present mistakes?

These are falsifiable mechanisms, not a diagnosis derived from human resemblance.

| Observation | Mathematical concern | Test or remedy |
| --- | --- | --- |
| First/last confusion | The command and boundary identity must survive the entire recurrent prefix. Current $\alpha_i$ is learned but constant across inputs. | Balanced command contrasts, boundary chains, and fresh length transfer. A future input-dependent retention gate is a separate architecture hypothesis. |
| Last returns a middle symbol | An ordered sequence is compressed into one bounded state; a delimiter may disturb the needed endpoint representation. | Count errors by selected input position, not just correct/incorrect. Compare append/prepend teaching without altering the core. |
| Correct training examples, poor new combinations | Minimizing empirical loss does not guarantee learning the operation rather than correlations of short strings. | Withhold whole strings and reversals across all commands; score longer strings separately. |
| New learning breaks old answers | A shared parameter displacement can help one task and hurt another. | Common rehearsal, conservative route updates, explicit retention checks. |
| More routes do not help | Capacity is not useful unless optimization assigns it a beneficial function. | Equal-update fixed-size rewiring versus bounded function-preserving initialization. |
| Similar-looking symbols are confused | The core receives UTF-8 bytes, not visual shapes. | Separate byte/encoding and logical-position errors; do not infer child-like visual cognition. |

Writing the recurrence as $s_t=F_\theta(s_{t-1},e_t)$ exposes the memory issue:

$$\frac{\partial s_T}{\partial e_j}
=\left(\prod_{t=T}^{j+1}\frac{\partial F_t}{\partial s_{t-1}}\right)
\frac{\partial F_j}{\partial e_j}.$$

Long chains of Jacobians can suppress or amplify information and its learning
signal. One cannot replace this expression with $\alpha^{T-j}$: message mixing,
activity-dependent gates, and normalization also contribute derivatives.
Bounded states do not prove adequate long-range memory. Nor is a single saliency
gradient a causal explanation of a prediction.

For forgetting, let $g_o=\nabla L_{old}$ and $g_n=\nabla L_{new}$. A plain
small gradient step gives the first-order approximation

$$L_{old}(\theta-\eta g_n)-L_{old}(\theta)
\approx-\eta\,g_o^Tg_n.$$

If the dot product is negative, an update that helps new examples can harm old
ones. With Adam, evaluate the actual displacement $\Delta\theta$ instead:
$\Delta L_{old}\approx g_o^T\Delta\theta$. Neither approximation proves
test-set preservation. This is why a final retention test cannot be omitted.

## 6. Tested pathway-change algorithms

### A. Smaller configuration changes, unchanged size

Let $\rho=(a,v,g,\phi)$ and let $\rho^*$ be Adam's proposed new routes:

$$\rho_{new}=\rho_{old}+0.25(\rho^*-\rho_{old}).$$

Other parameter groups keep their full update. This is an experimental
post-update damping rule; Adam's moments are not damped. It is not a guarantee
of less forgetting, since input/output mappings can still change substantially.

### B. Rewire a low-base-strength slot, unchanged size

Define base strength $b_{ir}=\operatorname{softmax}(a_i)_r\sigma(g_{ir})$,
choose $r_i=\arg\min_r b_{ir}$, and replace $S_{i,r_i}$ with the nearest
unused source. Keep its route parameter values and reset the corresponding
optimizer moments. There are still $NK$ slots. A low base gate can nevertheless
be important for particular inputs, so this has no preservation theorem.

### C. Split a route with an exact starting equivalence

For a route with score $q=a+\tanh(v)|u|$, make two copies with identical
source, phase, conductance and activity gain, and set

$$a_1=a_2=a-\log 2.$$

Then $e^{q_1}+e^{q_2}=e^q$, leaving the softmax denominator unchanged. Their
combined message is also unchanged:

$$\pi_1\sigma(g)e^{\mathrm{i}\phi}u+
\pi_2\sigma(g)e^{\mathrm{i}\phi}u
=\pi\sigma(g)e^{\mathrm{i}\phi}u.$$

Consequently each hop, each byte state, and the output map agree in exact
arithmetic before perturbation. This adapts the function-preserving expansion
principle from [Net2Net](https://arxiv.org/html/1511.05641v4), rather than
reproducing its full network-widening algorithm.

The tested growth variant splits one incoming slot per node once, halfway
through training, then perturbs new phases by +/-0.015 radians to encourage
different behavior. For one split contribution of coefficient $c$, its immediate
unnormalized message change has bound

$$|\Delta m|\le\tfrac12c|u|\,|\delta|,$$

using $|e^{\mathrm{i}\delta}-1|\le|\delta|$. This is a local bound for fixed
hop inputs, not an end-to-end accuracy guarantee. Later training can break the
equivalence. Existing optimizer moments are migrated; expanded slots start
with zero moments. Optimization trajectories need not remain equivalent.

### D. Candidate selection, outside the model

The mathematical research goal is not just minimum training loss:

$$\min_{\theta,S}\;L_{new}(\theta,S)+\lambda\,C(\theta,S)
\quad\text{subject to retention and device limits}.$$

The current experiment does **not** optimize that constrained objective
directly. It compares a finite set of candidates, ranks retention first and
fresh-question accuracy next, and reports resource costs separately.

```text
COMPARE:
    freeze one checkpoint including optimizer state
    seal disjoint teacher-selection, pathway-selection, and final questions
    train each teacher recipe from that checkpoint, on three teaching seeds
    seal the teacher choice using retention-first scoring
    train its pathway variants from the SAME starting checkpoint and budget
    seal the pathway choice and finalist list
    generate final answers without learning from them
    report accuracy, lost old answers, time, and all memory costs
    leave the live checkpoint untouched
```

The related ideas of [dynamic sparse reparameterization](https://proceedings.mlr.press/v97/mostafa19a.html)
and [systematic generalization tests](https://arxiv.org/abs/1711.00350) motivate
connectivity and composition experiments. They do not establish Kavi's success.
See the [prespecified comparison and results](../experiments/2026-09-04-teaching-and-pathways.md).

## 7. Size, computation, and finite memory

The parameter count for this implementation is

$$P=512N+512N+256+N+4NK=1025N+4NK+256.$$

At $N=64,K=4$: $P=66,880$, or 267,520 float32 parameter bytes. At $K=5$:
$P=67,136$, an increase of 256 parameters, or about 0.383%. Graph slots grow
25%, but whole-model parameter storage grows much less. Training also needs
gradients, two Adam moment arrays, step counters, graph indices, saved
activations, and the runtime itself. Small weight files do not imply equally
small process memory. Archived checkpoints and teaching records consume disk
even when they are not part of inference.

Per byte, sparse mixing costs approximately $O(HNK)$, while dense next-byte
readout costs $O(256\cdot2N)$. Sequential state is $O(N)$ per row; training
stores additional intermediate states across the bounded sequence. Exact wall
time must be measured: Python and runtime overhead can dominate this tiny core.

Reusing a circuit can compactly express a rule that covers many inputs. It
cannot retain arbitrary independent information without limit. With $M$ bits
of physical persistent state, at most $2^M$ distinct state configurations are
available. More than that many arbitrary histories must sometimes share a state.
The model may generalize a learned rule, but finite precision is not unlimited
exact memory. No information-conservation or thermodynamic identity in this
code turns knowledge into physical mass, energy, or gravity.

## 8. What remains a proposal

An input-dependent memory gate is a plausible next test:

$$\alpha_{t,i}=\sigma(\mu_i+u_i^Te_{t,i}+v_i^Ts_{t-1,i}).$$

With two real coordinates per node, this adds $4N$ parameters and recovers the
current gate when the new coefficients are zero. It could learn to preserve a
command or endpoint across delimiters instead of using one blend for every
byte. Whether it helps requires the same retention and new-length checks; it
is not implemented by the present experiment.

Other unimplemented tests include keeping input/output encodings fixed while
training routes to measure their contribution, measuring traffic rather than
base strength before rewiring, and proposing actual route merging with output
distortion checks. None is evidence of a solved language-learning problem.
The architecture's broad-intelligence objective remains an open research goal.

## 9. Later clarification: preserve abilities, not frozen parameters

The [adaptive-circuit response plan](ADAPTIVE_CIRCUIT_RESPONSE_PLAN.md) formalizes
the subsequent circuit/material analogy, including explicit state and resonance
equations. Those additional dynamics are proposals, not features measured below.

The [small-repair experiment](../experiments/2026-09-04-small-repair-connections.md)
adds eight context-dependent signal connections and a non-frozen comparison.
Its exact equations, diagram, and algorithm distinguish changes in configuration
from changes in behavior. The original circuit remains trainable in every
measured arm. An average reference-loss constraint steers harmful proposed
changes; it does not claim time travel, unlimited memory, or perfect retention.

In the intended vocabulary, a pathway is a transformation $\mathcal P$ of a
signal, and a junction combines or redirects transformations. A path is not
necessarily a single scalar edge weight. The current implementation represents
those transformations with learnable numerical settings; calling them pathway
configurations does not remove the fact that they are numerical parameters.
A fully discrete rewrite system without scalar learned coefficients would be
a different, not-yet-implemented architecture, not a renamed version of this one.
