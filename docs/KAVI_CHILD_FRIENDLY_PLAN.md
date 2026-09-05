# Project overview

Author: [Arnav123-s](https://github.com/Arnav123-s)

Kavi studies how a small program can learn useful procedures and keep improving them. A learned procedure is a sequence of operations that can be reused when a new problem has the same structure.

The first goal is to learn short list, string and arithmetic procedures from examples. When an answer is wrong, a verifier supplies a correction. The learner searches for a change that fixes the error while retaining earlier behavior. Repeated parts can become shared procedures.

The current repository contains early symbolic experiments and a small text network. They show limited learning, but the complete procedure-learning system still needs implementation. More teaching material alone will not close that gap.

The immediate milestones are a reproducible baseline, a typed interpreter, bounded program search, shared-library learning and independently checked retention. The [engineering specification](KAVI_ENGINEERING_SPECIFICATION.md) explains the mathematics, evidence and practical prospects.
