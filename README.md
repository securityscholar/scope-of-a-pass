# The Scope of a Pass: research artifact

This repository accompanies the Stage 1 proposal "The Scope of a Pass" and its technical appendix (Part II).

- `known-answer-audit/`: the realistic instrument. It generates empirical research tasks with planted defects and
  known answers, screens generated files for copied values, grades each run on four layers, runs the gate, and holds
  the results tables and the 26 turn-2 agent notes. Its README gives the commands; its tests run offline with
  `python3 tests/test_grade.py` and the other files in `tests/`.

All data are synthetic.
