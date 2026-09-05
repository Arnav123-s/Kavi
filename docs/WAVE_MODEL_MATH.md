# Recurrent text model mathematics

Author: [Arnav123-s](https://github.com/Arnav123-s)

These equations specify the earlier recurrent text core and its numerical weights. The [current structural learner](CIRCUIT_RUNTIME.md) uses a separate discrete gate representation and counterexample-guided search.

Implementation reference for `kavi/wave_core.py`.

### 3.1 Representation and parameter accounting

Let the input byte be x_t and the recurrent state be s_t. The default configuration has N = 64 nodes, K = 4 incoming slots per node and H = 2 mixing hops per byte. Each state coordinate has a real and an imaginary component.

$$x_t\in\{0,\ldots,255\},\qquad s_t\in\mathbb C^N.$$

| Stored quantity | Shape | Purpose |
| --- | --- | --- |
| Byte embedding E | 256 by 2N | Encode each input byte |
| Readout W and bias b | 256 by 2N and 256 | Predict the next byte |
| Source indices S | N by K integers | Select each incoming slot's source |
| Base logits a | N by K | Set routing preferences |
| Activity gains v | N by K | Condition routing on source magnitude |
| Conductances g | N by K | Bound transmitted strength |
| Phases phi | N by K | Rotate two-coordinate signals |
| Memory gates mu | N | Blend previous state and current input |

The source offsets are 0, 1, 3 and 7 modulo N. They are initial graph coordinates, with no demonstrated correspondence to conceptual regions.

$$P=2(256)(2N)+256+4NK+N=66{,}880.$$

The embedding and readout matrices contain 65,536 parameters, or 97.99 percent of the total. All parameters occupy 267,520 bytes at float32. The recorded initialized optimizer tensors occupy approximately 535,072 additional bytes. Gradients, activations, graph indices, Python objects, runtime libraries and checkpoints are extra. Counting only the route coefficients would substantially understate the model.

This accounting does not establish that the matrices provide 98 percent of the capability. Attribution requires controlled freezing or replacement experiments. It does establish that the present learned representation is not confined to executable routes.

### 3.2 Forward computation

Convert the embedding into a complex vector e_t and set alpha_i to the sigmoid of mu_i. The initial state for each byte is

$$z_i^{(0)}=\alpha_i s_{t-1,i}+(1-\alpha_i)e_{t,i}.$$

For each mixing hop, gather the source signals and compute a softmax across the K available slots.

$$u_{ir}=z_{S_{ir}},\qquad q_{ir}=a_{ir}+\tanh(v_{ir})|u_{ir}|,$$

$$\pi_{ir}=\frac{\exp(q_{ir})}{\sum_{r'}\exp(q_{ir'})},\qquad m_i=\sum_r\pi_{ir}\sigma(g_{ir})e^{\mathrm{i}\phi_{ir}}u_{ir}.$$

The hop adds a residual message and an input contribution, then normalizes the result.

$$\widetilde z_i=z_i+\tfrac12m_i+\tfrac14e_{t,i},\qquad z_i^{\mathrm{new}}=\frac{\widetilde z_i}{\sqrt{1+|\widetilde z_i|^2}}.$$

After H hops, flatten the real and imaginary coordinates in interleaved node order and compute the output logits. Define vec_R(s) as `(Re s_1, Im s_1, Re s_2, Im s_2, ...)`, matching the tensor layout in the implementation.

$$s_t=z^{(H)},\qquad \ell_t=W\operatorname{vec}_{\mathbb R}(s_t)+b.$$

Generation chooses the largest logit, feeds that byte back into the same network, and stops on newline or the output limit. Independent questions start from a reset sequence state. This is deterministic greedy generation for fixed parameters and input.

The softmax routes are numerically sparse in their available connectivity, but every allocated slot is evaluated. A very small gate does not skip its arithmetic. Sparse connectivity, sparse activation and sparse execution are different engineering properties.

### 3.3 Complex arithmetic and stability

A complex linear map has an exact real-coordinate representation.

$$ (A+\mathrm{i}B)(x+\mathrm{i}y)\ \longleftrightarrow\ \begin{bmatrix}A&-B\\B&A\end{bmatrix}\begin{bmatrix}x\\y\end{bmatrix}.$$

The benefit, if any, comes from the imposed structure, parameter sharing and optimization behavior. It must be compared with real-valued alternatives. The complex-network literature reports task-dependent results, including settings where real networks perform better. [Deep Complex Networks](https://arxiv.org/html/1705.09792v3).

The normalization ensures a bounded magnitude after each hop for finite inputs.

$$|z_i^{\mathrm{new}}|^2=\frac{|\widetilde z_i|^2}{1+|\widetilde z_i|^2}<1.$$

It does not establish contraction of the complete recurrent mapping, adequate memory, stable gradients or correct answers. Those properties depend on the Jacobian of the full recurrence, including activity-dependent routing. A bounded state can still lose the information required to distinguish first, middle and last positions.

### 3.4 Objective and learning

Answer-focused learning combines a prompt prefix with a verified answer and newline. Only target answer bytes contribute directly to the loss; the prefix influences them through recurrent state. Each example's loss is normalized by its answer length, and examples receive equal weight.

$$L(\theta)=-\frac1B\sum_{b=1}^B\frac1{|T_b|}\sum_{t\in T_b}\log p_\theta(y_{b,t}\mid p_b,y_{b,<t}).$$

Backpropagation through time computes gradients. Their global norm is clipped to one, and Adam updates the parameters. Training uses supplied earlier answer bytes when predicting later answer bytes. Evaluation generates its own bytes. A low training loss therefore does not guarantee a correct complete generated answer.

The `learn` method uses truncated sequence segments; `learn_answers` carries gradients through the full bounded example. Four independent examples can be processed together or in smaller microbatches if their gradients are accumulated before one optimizer step. Four separate Adam steps define a different algorithm.

### 3.5 Computational cost

For a sequence of length T, the sparse mixing work scales approximately with T H N K. The dense readout adds work proportional to T N V, where V is the byte vocabulary size. Automatic differentiation also retains intermediate computations across training time. A sparse recurrent graph can therefore have a small parameter array while still requiring substantial execution and runtime memory.

The current implementation loops through bytes in Python and performs many small tensor operations. On this device, dispatch overhead and memory traffic may dominate an individual arithmetic operation. Profiling is needed before proposing GPU execution, more nodes, additional hops or low precision. Smaller parameter growth is not evidence of a smaller runtime cost.

See the [full specification](KAVI_ENGINEERING_SPECIFICATION.md) for experiments, retention and alternative architectures.
