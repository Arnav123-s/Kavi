# Correctness of the acquired addition circuit

Author: [Arnav123-s](https://github.com/Arnav123-s)

7 September 2026. Mathematical argument for the existing artifact; no change to learning or execution. The [full study](CERTIFIED_ARITHMETIC_AND_SOFTWARE_EFFICIENCY.md) audits external claims and records deferred recommendations.


### 2.1 Contract

Let A and B be nonnegative integers. Their bits arrive least significant first. The circuit has one carry bit, initialized to zero. Each frame computes its emitted bit and next carry from the same old carry. Gates preserve Boolean values. After all significant input positions, one frame containing two zero input bits flushes the final carry. Emitted bits occupy distinct output positions.

For every local input triple, require:

$$e(a,b,c)+2t(a,b,c)=a+b+c,\qquad a,b,c\in\{0,1\}.$$

Here e and t are Boolean-valued output functions. There are exactly eight triples. The eight-row check is exhaustive for these local functions; its size does not grow with operand length.

![Addition certificate and streaming contract](figures/addition-proof-flow.svg)

### 2.2 Invariant with an unambiguous index

Let c at index i be the carry before processing bit i. Let R at index i contain exactly the i bits already emitted. Define:

$$R_i=\sum_{j=0}^{i-1}e_j2^j,\qquad c_0=0,\quad R_0=0.$$

The invariant before frame i is:

$$R_i+2^ic_i=(A\bmod2^i)+(B\bmod2^i).$$

At i=0 both sides are zero. Assuming the invariant, write a_i and b_i for the current operand bits. The next output prefix and the transition identity give:

$$\begin{aligned}R_{i+1}+2^{i+1}c_{i+1}&=R_i+2^i(e_i+2c_{i+1})\\&=R_i+2^i(a_i+b_i+c_i)\\&=(A\bmod2^{i+1})+(B\bmod2^{i+1}).\end{aligned}$$

Thus induction proves the invariant at every finite position. Choose w at least one and large enough to contain both operands. Before flushing:

$$R_w+2^wc_w=A+B.$$

At the zero-input frame, the local identity becomes e_w+2c_(w+1)=c_w. Since both outputs are bits and c_w is zero or one, necessarily e_w=c_w and c_(w+1)=0. Therefore:

$$R_{w+1}=A+B.$$

This proves exact addition for every finite operand width in the abstract streaming model. It is not induction over training examples and does not depend on a probabilistic extrapolation from the eight-bit audit.

### 2.3 Why the assumptions matter

A nonzero initial carry changes the result. Omitting the final frame loses an overflow bit: with one-bit inputs 1 and 1, the first emitted bit is zero and the carry is one. Computing one output from a newly updated carry changes the transition semantics. A non-Boolean next-state value invalidates the final-flush reasoning.

In `kavi/circuit_core.py`, the constructor checks the allowed gate operations and reference structure. `execute` reads old state for both outputs, initializes state and result to zero, and uses one final padded frame. It constructs the result with bitwise OR; because each Boolean output occupies a distinct position, that operation equals the sum defining R. Python's mathematical-integer behavior is assumed within available resources.

The runtime rejects inputs longer than 4,096 bits. An output may have 4,097 bits. The proof describes the algorithm independently of that guard; it does not override the guard or prove the interpreter, operating system, memory subsystem or underlying hardware correct.

### 2.4 What is already certified and what remains empirical

`kavi/circuit_runtime.py:local_invariant` already checks all eight rows after selection and records the graph digest. `kavi/procedure_optimizations.py:addition_certificate` checks the same identity before the supplied multiplication compilation. The 5 September experiment already stated that the identity supports an induction under the documented executor. This study supplies the complete argument and audits the existing artifact without changing either checker.

The canonical graph has five gates and 321 serialized bytes. Its SHA-256 is recorded in the accompanying audit. The learning run exposed 81 foundation pairs and 48 carry-producing pairs. Recorded foundation counterexamples were two, one and one across the three seeds; each repair used six. Counterexamples alone are not the full supervision received by the search and verifier.

The 65,536-pair audit remains useful. It checks the concrete integration of loading, framing, execution and decoding and can catch implementation mistakes outside the local theorem. Proof and tests have different responsibilities. Neither is a reason to erase the other from the record.

The defensible claim is: **Kavi acquired a 321-byte addition transition whose complete local truth table, together with the declared streaming contract, proves exact addition for arbitrary finite widths. The current implementation accepts inputs up to 4,096 bits.** The small artifact excludes the executor, search catalog, teacher, verifier and logs. The experiment does not demonstrate a general arithmetic learner free of supplied structure.
