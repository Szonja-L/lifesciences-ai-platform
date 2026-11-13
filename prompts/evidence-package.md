Monthly evidence package for month N (replace N before pasting). Follow CLAUDE.md. Budget: the last two hours of the month.

1. Read PROGRESS.md, CHANGELOG.md "Unreleased", docs/interview-notes.md entries since the last package, and docs/evaluation/ files changed this month.
2. Move the CHANGELOG "Unreleased" entries under a new version heading with today's date (v0.N, or the tag named in the phase file).
3. Update the README status section: what works now, how to run it, what is next.
4. Write docs/evidence/month-N.md with these sections: What was built (bullets, each linking a file or module); What was measured (table, each number linking the script that produced it); What was learned; Known limitations; Next month. Only measured numbers; no projections.
5. Write the demo instructions: which screens to show in which order for a 60-second GIF. I record the GIF myself with ScreenToGif and save it to docs/evidence/month-N.gif; add the link.
6. Draft one LinkedIn post (under 1,300 characters, first person, plain, no hashtag wall, at most three hashtags) in docs/evidence/month-N-linkedin.md. It describes what was built and one measured result, names Clementine only as agreed, and never calls anything a prototype for a client.
7. Draft two CV bullets in docs/evidence/month-N-cv-bullets.md: plain what, with what, achieved; an outcome on each; only measured claims; the words synthetic, demo, mock and test data do not appear; no em dashes. These are drafts; the final wording is done in the Job Scout workspace.
8. Update PROGRESS.md and propose the commit message and the tag command: `git tag -a v0.N -m "..."` then `git push --tags`.
