# Tutor skill `learn`

A copy of the Claude Code skill that runs the tutor. The working copy lives in `ea-personal/.claude/skills/learn/` and is copied here on every commit (pre-commit hook), so edit it there, not here.

To use it in your own setup, copy `skill/learn/` to `.claude/skills/learn/` in the folder where you start Claude Code, put a course folder next to it (this repository is one), and ask to study. The commands in `data/course.md` assume the course folder sits at `projects/<course>/` below that folder, so the scripts are at `../../.claude/skills/learn/scripts/`.
