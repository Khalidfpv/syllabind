# Contributing

Thanks for helping. Keep changes small, tested and documented.

## Set up
```bash
pip install -r skills/syllabind/scripts/requirements.txt
python -m playwright install chromium
```

## Before you open a pull request
1. Build, export and check the example. Every command must pass:
   ```bash
   python skills/syllabind/scripts/build.py skills/syllabind/example
   python skills/syllabind/scripts/export.py skills/syllabind/example --dest out
   python skills/syllabind/scripts/verify_html.py out
   python skills/syllabind/scripts/check_pdf.py "out/Sample Course 2026.pdf" --course skills/syllabind/example
   claude plugin validate . --strict
   ```
2. If you change the look, open the HTML and the rendered PDF pages, and attach before/after screenshots to the PR.
3. Update the docs in the same PR: `SKILL.md`, `reference/*.md`, the example course and `CHANGELOG.md`.
4. Bump `version` in `.claude-plugin/plugin.json` for every release, so plugin users get the update.

## Conventions
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- One logical change per commit.
- Scripts take every path as an argument. Never hard-code machine paths, user names or brand names.
- Generated folders (`build/`, `out/`, `dist/`) are never committed.
- `SKILL.md` frontmatter may only use `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
  Other keys break the claude.ai upload. `tools/package_skill.py` checks this.

## Releasing
1. Update `CHANGELOG.md` and bump the version in `.claude-plugin/plugin.json`.
2. `python tools/package_skill.py` creates `dist/syllabind-<version>.zip`.
3. Tag `v<version>` and attach the zip to a GitHub release.
