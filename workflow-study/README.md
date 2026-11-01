# The Scope of a Pass — W2 reviewer materials

This is an anonymized inspection copy of the original October 28, 2026 Workflow Study release. It contains existing research evidence, not a new experiment. Recovery used static file inspection, hashing, copying and metadata redaction only. No model calls, experiments, grading, analysis, or result reproduction were run for this copy.

## What the study did

The locally frozen W2 protocol compares how an interpreter's conclusions depend on the records and verification messages it receives. Twelve synthetic tasks span four mathematical structures. Two requested configurations, `gpt-6-astra` and `gpt-6.1-sol`, both at high reasoning effort, follow six information policies. Together these produce 144 interpreter (receiver) episodes, with 24 shared source analyses and 48 numerical-checker contexts. A receiver episode is one downstream task/condition, not an independent source study.

The six policies are a shared-transcript researcher; full delegated records; analyst-selected records; and deliberately removed design records accompanied by a general receipt, a scoped numerical receipt, or a general receipt with a separate caution. An interpreter can request one archived design record. An arithmetic pass verifies a numerical calculation; scientific support additionally depends on the assumptions and evidence actually received.

The existing records report 144 scientifically supported final answers and no unsupported final causal claims. They retain a distinct original literal-citation contract, which flagged ten uses of a field that was actually present in the packet. Its original results and the later disclosed citation audit are both included. These statements describe the saved release; they are not fresh validation or evidence of a general model ranking. Tasks and conditions share upstream information, and four structures do not become 144 independent structures.

## Start with these files

- `Proposal.pdf` and `Technical_Supplement.pdf` explain the question, workflow, results and limits. Their prose, tables and figures have not been rewritten. Word and Markdown versions are also included.
- `index.html` is the original offline viewer. It can be inspected locally without a server. It was copied, not rebuilt.
- `workflow/protocol_W2.json` contains the frozen protocol, configurations, ordering, stopping rule and original source fingerprints.
- `workflow/data/cases.json` contains all constructed cases, source records, seeds, latent worlds and answer keys. These are reviewer evidence, not a file that was supplied wholesale to the models.
- `workflow/evaluator/information_sets.json` contains the saved reference regimes and witnesses used to assess which conclusions the available information can support.
- `workflow/workflow.py` defines prompt templates, packets, policies and retrieval. The `core/` code contains original task, reference and scoring logic. Other Python files preserve the original execution, analysis, citation audit and validation procedures. None was imported or executed for this recovery.
- `workflow/runs/` contains all saved W2 requests, schemas, final responses, events, standard-error streams, checkpoints, executions, packets and decisions. `request.json` contains the actual serialized prompt with the experimental instruction prefix. Analyst-generated Python is retained inside the corresponding responses, and its recorded outputs are in `analyst_execution.json` and `upstream.json`.
- `workflow/results/` contains all existing tables and audits. `episodes.csv` links results by model, case and condition; `upstream.csv` records shared artifacts; `model_calls.csv` accounts for study calls. `results.json`, `summary.csv` and `paired_contrasts.csv` retain the strict scoring. `reporting_results.json`, `scientific_summary.csv`, `scientific_paired_contrasts.csv` and `citation_audit.csv` retain the separately labeled post-run audit.
- `workflow/analysis_history/` preserves the original analysis and audit chronology. `workflow/run_logs/` preserves both W2 worker logs. `figures/` contains existing images; `publication_source/` contains optional original formatting/viewer source.
- `historical_records/` contains the original README, original launcher and existing W2 validation logs, explicitly historical. The validation JSON is labeled as an excerpt; earlier-study sections and an identifying local output path were excluded or anonymized.
- `BUILD_ENVIRONMENT.json` records software versions, model configurations and the standard-library science runtime. `RELEASE_INVENTORY.csv` gives each included file's purpose. `ANONYMIZATION_NOTE.md` explains privacy changes and limitations.

## Following a run

Locate a row in `workflow/results/episodes.csv`, then open `workflow/runs/<model>/<case_id>/<route>/episode.json`. Its initial and final input fingerprints point to the corresponding `initial/` and, when retrieval occurred, `after_retrieval/` request and response files. The initial packet, optional archive response and final packet show the information available at each step. The case-level analyst and two checker directories contain the shared upstream requests and responses. All 144 episode paths, all 270 study-call records, the separate access check, and all 271 recorded attempts are retained. No run was selected or dropped because of its outcome.

All serialized experimental prompts, final response files, numerical execution records, episode records and existing result tables retain their original bytes. Event session identifiers and one account-related token in a logged plugin-catalog failure were anonymized. The error itself remains inspectable. No private reasoning text occurred in the saved W2 event streams; reasoning-token counts remain.

## Historical reproduction procedure and present limits

The original release intended Python 3.10+ and standard-library execution of `python -B reproduce.py --out <new-output-directory>` from a complete original release. That procedure checks hashes, runs the original engineering and citation-audit tests, validates information regimes, reconstructs numerical artifacts and regrades recorded episodes. It then extracts and separately checks an earlier-study archive. Optional publication builds additionally use the document and plotting software recorded in `BUILD_ENVIRONMENT.json`.

**The original all-in-one launcher is preserved for documentation, not certified runnable in this reviewer copy.** The earlier-study archive is intentionally absent so that this package contains only W2 materials. Machine-local paths in two source files have been replaced by neutral relative placeholders. Original frozen source hashes still describe the unmodified source release, so checks involving the redacted adapter will fail; those historical hashes have not been rewritten. The original `RUN_ME.cmd` is under `historical_records/RUN_ME_ORIGINAL.cmd` to avoid presenting it as a current launcher. No substitute analysis, grading, reproduction script, or updated result was created.

The existing validation logs and W2 excerpt document an earlier successful reproduction of the original release. They do not certify execution of this anonymized copy. This copy supports inspection and independent reimplementation, with the original scientific code and saved evidence provided transparently.

## Integrity and context coverage

`SHA256SUMS_REVIEWER.json` covers every regular file in this reviewer directory except itself, with relative paths, lengths and SHA-256 hashes. It is a new manifest of the reviewer copy, not the original 2,157-entry manifest. `RELEASE_INVENTORY.csv` includes itself and the new manifest. Private source locations, the original verification report and detailed redaction mappings are not included.

The actual serialized prompts and the instruction-building code are preserved. Separate provider/system/developer messages or unrecorded CLI context are not present in this release, and no claim is made that it is a complete account-level transcript. General conversations, private project management and field-log entry text were not imported. The prior-study archive and its drafts are omitted; any historical discussion of those earlier studies in the unchanged proposal or supplement is not independently supported by this W2-only package. Anonymization reduces identifying material but cannot guarantee anonymity against outside information.
