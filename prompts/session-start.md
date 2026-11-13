Start of session. Follow CLAUDE.md.

1. Read PROGRESS.md. Identify the current task id.
2. Open prompts/phase-N.md for the current phase and read only the block for that task.
3. Inspect only the files and folders that task names, plus `git log --oneline -5` and `git status`. Do not read PROJECT_PLAN.md in full; open only the sections the task block lists under "Reads".
4. Report, in this order: what exists that the task touches, what the task will produce, the design (files to create or change, dependencies to add and why, trade-offs), and anything in the task block that no longer matches the repository.
5. If the task block says "Model: Opus" and you are not running as Opus, say so before anything else, and stop.
6. Stop and wait for my approval. Do not write application code before I answer.

If PROGRESS.md and the repository disagree, trust the repository and say what differs.
