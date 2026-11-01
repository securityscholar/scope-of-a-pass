# The Scope of a Pass

Code, data, and recorded results for the two research prototypes described in the proposal and technical appendix.

- [`supplement/`](supplement/): the current technical appendix in Word and PDF.
- [`known-answer-audit/`](known-answer-audit/): the realistic research task, in which an agent builds a firm-year dataset and estimates one regression. Includes the task generator, checking and scoring code, results tables, and 26 agent notes.
- [`workflow-study/`](workflow-study/): the October 28 W2 exact-inference study, with 144 interpreter episodes, recorded prompts and responses, execution outputs, code, and results.

Start with the technical appendix. The W2 [`viewer`](workflow-study/index.html) lets you inspect its tasks and recorded runs; download the file and open it in a browser. Each prototype's folder has its own README with file descriptions and commands.

## Reproduction requirements

The W2 reproduction script expects its original path settings and an earlier pilot archive that is not included here. Rebuilding the realistic-task tables requires run folders, answer keys, and transcripts that are withheld for privacy. The saved tables and agent notes are available for inspection.

All experimental task data are synthetic. The [`field-record summary`](known-answer-audit/field/) contains counts and dates; the entry text remains private. The W2 [`file inventory`](workflow-study/RELEASE_INVENTORY.csv) and [`anonymization note`](workflow-study/ANONYMIZATION_NOTE.md) describe the shared materials.
