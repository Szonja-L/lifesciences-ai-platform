# Prompt kit: how to run this programme with Claude Code

This folder holds everything needed to run the programme one session at a time. The reference plan is `PROJECT_PLAN.md`; the running state is `PROGRESS.md`.

## The rules in one place

- **One task per session.** A task is one block in `prompts/phase-N.md`, about 1-3 hours. Never a whole phase.
- **Fresh session every task.** Open Claude Code in this folder, do the task, close or `/clear`. `PROGRESS.md` carries the state across sessions, not the chat history.
- **Model.** Sonnet 5.5 by default. Switch to Opus 5.5 with `/model` only when a task block says "Model: Opus", for an ADR, or after two failed Sonnet attempts at the same bug. Record Opus use in `PROGRESS.md`.
- **No subagents, no parallel builds.** Sequential tasks that Szonja reads one diff at a time. CLAUDE.md enforces this.
- **Claude writes, Szonja reviews.** After every task she runs `prompts/review-checklist.md` herself before committing.
- **Pro subscription budget.** Roughly 3-4 Sonnet sessions or 1 Opus session per 5-hour window. Six to ten sessions a week covers 20 hours.

## Step 0 (once): GitHub remote

Create an empty public repository named `lifesciences-ai-platform` on GitHub (no README, no .gitignore), then:

```
git branch -M main
git remote add origin https://github.com/<your-login>/lifesciences-ai-platform.git
git push -u origin main
```

## A session, step by step

1. Open `lifesciences-ai-platform` in its own VS Code window. Start Claude Code. Set the model.
2. Paste the whole of `prompts/session-start.md`.
3. Claude reads `PROGRESS.md`, opens the current task block, inspects only the files it touches, and reports findings and a design. It stops there.
4. Approve, or adjust the design, in one or two sentences.
5. Claude implements, runs the checks, and reports real results.
6. Paste the whole of `prompts/session-end.md`.
7. Run `prompts/review-checklist.md` yourself. Commit with the message Claude proposed. Push. `/clear`.

## Files

| File | Who uses it | When |
|---|---|---|
| `session-start.md` | pasted to Claude | start of every session |
| `session-end.md` | pasted to Claude | end of every task |
| `phase-0.md`, `phase-1.md` | read by Claude | detailed task blocks for month 1 |
| `phase-2.md` to `phase-8.md` | read by Claude | task lists; expanded at phase start |
| `plan-phase.md` | pasted to Claude | once, at the start of each phase from 2 on |
| `evidence-package.md` | pasted to Claude | last task of every month |
| `review-checklist.md` | Szonja | after every task, before commit |

## When something goes wrong

- Claude starts writing code before reporting: stop it, paste `session-start.md` again.
- A task grows past 3 hours: have Claude split it into N.Na and N.Nb in the phase file, finish the first half, run `session-end.md`.
- CI is red after a push: next session's task is "make CI green", nothing else.
- The plan no longer fits reality: write an ADR in `docs/decisions/`, then change the plan. Do not drift silently.
