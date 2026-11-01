# Update v10.4 (31 Oct 2026). Supersedes v10.3 (and contains it).

Handover package so the work can continue from Claude Code or any new session.

What changed on top of v10.3:
- NEW  CLAUDE.md          rules and build instructions, auto-read by Claude Code
- NEW  OPERATIONS.md      full handover: goal, people, accounts, site map, routines, content rules, events, metrics, open tasks, version log
- NEW  tools/build.py, tools/articles.py, tools/notify.py, tools/README.md   the generator and the Bing notifier, now inside the repo
- NEW  .vercelignore      keeps tools/ and the docs out of the deployed site

Upload: everything in this folder, keeping the insights/, tools/ and assets/ folders. Commit to main. Then delete case-studies/mighty-warners.html in a second commit.
Check after push: https://www.samuraconsulting.com/answer-engine-optimization-dubai
