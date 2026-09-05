# Mechanism comparison

Author: [Arnav123-s](https://github.com/Arnav123-s)

The [discrete runtime](CIRCUIT_RUNTIME.md) provides a concrete structural baseline: learned Boolean gates under an engineered streaming executor. Proposed physical replacements should compare against its measured operation, cost and retention before claiming an advantage.

Each proposed replacement needs a computational role and a simple control. Similarity to a physical process does not establish a learning advantage.

| Component | Proposed alternative | Necessary comparison |
| --- | --- | --- |
| Input segmentation | Learned multiscale events | Fixed bytes and explicit scalar segmentation |
| Dense mixing | Sparse typed routing | Equal-budget fixed graph and small recurrent model |
| Fixed depth | Adaptive settling | Equal total executed steps |
| State normalization | Energy-based constraints | Stability and retained information |
| Uniform update rate | Local clocks | Latency and quality under equal work |
| Gradient learning | Local equilibrium or eligibility update | Gradient accuracy and end-to-end cost |
| Monolithic storage | Program library and explicit memory | Complete serialized and retrieval cost |
| Capacity expansion | Verified splitting and consolidation | Transfer and retention after all changes |

Section 10 of the [specification](KAVI_ENGINEERING_SPECIFICATION.md) covers the ML components. Section 9 derives the physical constraints, and Appendix B defines the remaining hypotheses and rejection tests.
