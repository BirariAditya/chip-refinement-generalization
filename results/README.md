# Results policy

No real-circuit experiment results exist in this repository yet. Do not create zero-filled result tables that look measured.

For every future run save `result_type` (`pilot`, `validation`, `final_test`, or `illustrative`), design/family/split, source hashes, initializer artifact hash, method/config/checkpoint, training seed and evaluation seed, hardware/thread limits, phase durations, objective calls, complete passes, pre/post feasibility, metrics with units/stages, failure reason and output hashes. Missing values are `null` or `not_measured`, never zero.

Keep paper-reported findings in the literature documents. Synthetic toy output is illustrative. Save large real placement files, datasets and checkpoints outside Git, with acquisition instructions and content hashes. Freeze the test configuration before final runs; preserve failed runs and regression cases.
