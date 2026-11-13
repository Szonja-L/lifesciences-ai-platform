End of task. Do these in order and show real output, not summaries of output.

1. Run the checks: ruff, mypy, pytest (and `snakemake --dry-run` once a pipeline exists). Paste the final lines of each. If anything fails, fix it or say clearly that it is left failing and why.
2. `git status` and `git diff --stat`. Confirm no `.env`, data, uploads or generated results are staged.
3. Update PROGRESS.md: move the task to Done with today's date, set the next task id, record any open question for me, record the model if it was not Sonnet.
4. Append one line to CHANGELOG.md under "Unreleased".
5. Append to docs/interview-notes.md a block for this task: what was built, why this design, one trade-off, one thing that would break if done differently, and one question an interviewer could ask with a two-sentence answer. Five to eight lines total.
6. If this task made an architectural choice, write or update the ADR in docs/decisions/.
7. Propose one commit message (first line under 70 characters, then a short body). I commit and push myself.
8. End with the standard report from CLAUDE.md rule 18 and name the next smallest task.
