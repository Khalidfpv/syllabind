# tools

Maintainer scripts, not part of the skill itself.

| Script | Purpose |
|---|---|
| `package_skill.py` | Checks `SKILL.md` against the claude.ai limits and writes `dist/syllabind-<version>.zip` (one top-level `syllabind/` folder). |
| `make_readme_images.py` | Renders the sample course (web at desktop and phone size, plus PDF pages) and composes `docs/images/showcase-web.webp` and `showcase-pdf.webp`. Usage: `python tools/make_readme_images.py out` after `export.py`. Needs `numpy` in addition to the skill requirements. |
