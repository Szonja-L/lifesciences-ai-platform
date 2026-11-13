# Review checklist (for Szonja, after every task, before committing)

About ten minutes. The point is that you can defend every line in an interview and that nothing private leaves the machine.

1. Run `make check` yourself in the terminal. Do not trust the pasted output.
2. Run the thing: start the API or the app, or run the pipeline on the fixture, and click or call what the task added.
3. `git status`. Nothing staged that should not be: no `.env`, no `uploads/`, no `data/raw/`, no pipeline results, no PDFs outside `tests/fixtures/`.
4. `git diff` file by file. For each new module ask yourself: what does it do, why here, what calls it. If you cannot answer, ask Claude "explain this file as if I were asked about it in an interview" before committing.
5. Ask Claude one "why this way and not that way" question about the design. Write the answer into docs/interview-notes.md if it is not already there.
6. Check PROGRESS.md was updated and CHANGELOG.md has a new line.
7. Commit with the proposed message. Push. If CI goes red, the next session's only task is to fix it.
8. `/clear` the session.

Once a week, also:
- Read docs/interview-notes.md from the top and delete or merge repeated entries.
- Check the Anthropic console spend against `LLM_MONTHLY_BUDGET_EUR` (from Phase 2).
- Write three lines in docs/evidence/week-N.md: what was done, what was hard, what the next smallest task is.
