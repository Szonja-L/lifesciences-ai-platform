Phase planning session. Follow CLAUDE.md. Model: Opus 5.5 for this session.

1. Read PROGRESS.md and confirm which phase starts now.
2. Read prompts/phase-N.md for that phase (the task list and notes) and the PROJECT_PLAN.md sections it names under "Reference". Read prompts/phase-0.md once as the format example.
3. Inspect the repository: `git log --oneline -20`, the package layout, existing tests, CHANGELOG.md, the last evidence package in docs/evidence/, and any ADRs that affect this phase.
4. Rewrite the task list in prompts/phase-N.md into detailed task blocks in the exact format of phase-0.md: Task id and title, Model, Goal, Reads, Produces, Acceptance, Do not. Keep each task to 1-3 hours. Split tasks that are larger. Keep the phase prompt from the plan at the top unchanged.
5. Flag, in a "Changes from the plan" section at the bottom of the phase file, anything in PROJECT_PLAN.md that no longer fits what the repository has become, with a one-line reason each. Do not change PROJECT_PLAN.md; propose an ADR if the change is architectural.
6. Update PROGRESS.md: current task = N.1.
7. Do not write application code in this session. End with the standard report and the sentence "Next session: task N.1 with model X".
