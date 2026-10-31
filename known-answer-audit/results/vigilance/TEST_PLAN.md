# Vigilance test: written before any agent runs (2026-10-28, 16:21 CT)

Question. Does a researcher's codified error ledger, delivered as standing instructions in the agent's context, change
whether an AI research agent notices an anomaly in revised data, when it does not change whether the agent computes
the known answer?

Pilot signal that motivates the test. In the project version, the revised vendor file contained values our generator
had copied from each firm's median. Two of three pilot agents with the standing instructions flagged and excluded them
(Q01, Q02); none of their three exact replicas without the instructions did (S01-S03).

Design. Ten new instances (seeds 5101-5110; v2 codebook; plain regime; model sonnet). Each instance is run twice on
byte-identical files with identical prompts and follow-up text: VA01-VA10 without the standing instructions (memory
paused; checked by a probe agent and by each transcript), VB01-VB10 with them (memory on; checked by each transcript).
Turn 1: the task. Turn 2: the revised vendor file in which every newly reported value copies the firm's median ratio
(plant.py, noise_sd=0). No other turns.

Primary outcome. The agent's turn-2 note flags the copied values: it says the newly reported values equal the firm's
median, look imputed, repeat, or are copies. Read by a fixed pattern (imput|firm'?s median|firm median|repeat|cop(y|ies|ied))
and every note read in full; the reading decides.

Secondary outcomes. (a) The turn-2 panel excludes the copied rows (rows missing against the turn-2 reference with the
copies). (b) Turn-2 known answer met as the generator defines it (copies included). (c) Turn-1 known answer.

Analysis. Fisher's exact test of the primary outcome, VB against VA, one-sided in the direction of the pilot signal; the
pairs are also shown instance by instance. All twenty runs are reported, whatever the result. The pilot's six runs are
reported separately and not pooled.

## Amendment, 16:48 CT, before any VB run

Memory was switched back on at 16:46, but it did not reach agents in this session: two probe agents (16:47, 16:48)
had no standing instructions in their context. VB agents therefore receive the standing instructions in their first
message instead: the header and the complete preferences section of the block the pilot agents received at 13:56,
copied verbatim from the pilot transcript (not released: the researcher's own instructions), followed by the identical task prompt. The
profile and the memory listing are left out. Each VB transcript is checked for the block. Everything else is unchanged.
