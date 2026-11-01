# The Scope of a Pass: research artifact

This repository accompanies the Stage 1 proposal "The Scope of a Pass" and its technical appendix (Part II).

- [`supplement/`](supplement/): the current technical appendix, with corrections to artifact locations, reproduction coverage and privacy disclosures. The proposal has not been changed.
- [`known-answer-audit/`](known-answer-audit/): the realistic instrument. It generates empirical research tasks with planted defects and known answers, screens generated files for copied values, grades each run on four layers, runs the gate, and holds the results tables and the 26 turn-2 agent notes. Its existing code and data are unchanged.
- [`workflow-study/`](workflow-study/): the separately preserved October 28 W2 exact-inference study. It contains 144 interpreter episodes, 270 study-call records plus a separate access check, the actual recorded prompts and responses, execution outputs, original code, and existing results. Start with its [`README.md`](workflow-study/README.md), [`protocol`](workflow-study/workflow/protocol_W2.json), or [`offline viewer`](workflow-study/index.html).

The two prototypes use different tasks and model configurations. Their runs and results remain separate. Documents inside `workflow-study/` are historical W2 documents, not the current two-prototype proposal or appendix.

## Reproduction coverage

The W2 materials are an anonymized copy recovered from a verified original release. All 271 saved requests are byte-identical to that source; all interpreter episodes, recorded attempts, saved scientific responses and results were retained. Its [`reviewer manifest`](workflow-study/SHA256SUMS_REVIEWER.json) verifies the shared files, excluding itself; it is not the original 2,157-entry manifest.

The original W2 reproduction driver is preserved as historical source, **not as a working one-command launcher for this copy**. Machine-local paths were anonymized, original source-freeze hashes were retained, and a nested earlier-study archive was excluded. The original driver's combined procedure therefore cannot run unchanged. Existing validation records are historical and do not certify execution of this anonymized copy. No experiments, model calls, grading or result reproduction were rerun during recovery or this repository update.

The realistic instrument's saved tables and 26 notes remain in `known-answer-audit/results/`. Its existing generator, tests and analysis scripts are provided, but historical run folders, answer keys and raw transcripts needed to rebuild all reported tables are not included. Some transcripts contain private research context, including standing instructions. They are withheld; this repository does not promise their later publication. The public copy consequently does not permit full inspection of that context or independent regrading of every realistic-task run.

All experimental task data are synthetic. The `known-answer-audit/field/` files contain aggregate field-record summaries; entry text is not shared. Private correspondence, account histories, recovery notes and identifier mappings are excluded. See the W2 [`anonymization note`](workflow-study/ANONYMIZATION_NOTE.md) and [`file inventory`](workflow-study/RELEASE_INVENTORY.csv) for its coverage and limitations.
