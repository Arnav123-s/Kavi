# Typed program acquisition

Author: [Arnav123-s](https://github.com/Arnav123-s)

Status: proposed implementation of one acquisition mechanism within the [adaptive dataflow circuit design](ADAPTIVE_DATAFLOW_CIRCUIT.md).

The learned object is a typed executable program and a library of acquired subprocedures. A primitive defines its input types, result type, behavior, failure cases and execution cost. Candidate paths must type-check before execution.

## Acquisition

Start with a small grammar of list, scalar, Boolean and integer operations. Supply examples and independently verified answers, while withholding the target program. Search using type-directed enumeration and bounded local edits. A failure produces a counterexample that narrows the candidate set.

Use bounded execution and explicit timeout results. Search failure within a budget does not prove that no program exists. A learned proposal policy may later order candidates, but the verifier remains responsible for checking them.

## Reuse and consolidation

After solving several tasks, identify repeated structure and propose a shared procedure. Compare complete description length, runtime and adaptation cost on new tasks. A compact library is useful when its abstractions transfer beyond the programs used to create it.

Equivalent rewrites preserve behavior, including existing errors. Repair changes behavior and requires a separate correctness check. The [full formal specification](KAVI_ENGINEERING_SPECIFICATION.md) gives the objective, execution semantics and experiment design.

## Related work

[DreamCoder](https://people.csail.mit.edu/asolar/papers/EllisWNSMHCST21.pdf) is a close research relative of this program-and-library acquisition mechanism. [babble](https://arxiv.org/html/2212.04596v1) and [Stitch](https://arxiv.org/html/2211.16605v2) are especially relevant to library consolidation. [Syntax-guided synthesis](https://www.cis.upenn.edu/~alur/SyGuS13.pdf) provides a framework for grammar-constrained acquisition and counterexamples. The broader adaptive circuit also concerns changes to the executing graph, discussed in the [research comparison](ADAPTIVE_DATAFLOW_CIRCUIT.md#8-closest-research-relatives).
