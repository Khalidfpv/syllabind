# Changelog

All notable changes are listed here. Versions follow [Semantic Versioning](https://semver.org/).

## [1.0.3] — 2026-10-19
### Changed
- The setup smoke test now runs in a temporary copy, so nothing is written into the installed skill folder.

## [1.0.2] — 2026-10-19
### Fixed
- `SKILL.md` frontmatter was invalid YAML in 1.0.1 (a `: ` inside the description), which could stop the skill from loading. Use 1.0.2 or later.
- Long unbreakable text (such as a URL) made a module scroll sideways on phones. It now wraps.
- Module and cover counters read "1 image" / "1 diagram" instead of "1 images".
### Changed
- `tools/package_skill.py` now parses the frontmatter with a real YAML parser, so CI fails on this kind of mistake.
- `verify_html.py` tests every module at phone width, not only the first.
- `check_pdf.py` reports headings stranded at the bottom of a page; the print stylesheet keeps a heading with the content after it.
- Scripts print a one-line fix when a Python package or Playwright's Chromium is missing.
- PDF code uses the supported `pymupdf` import (the old `fitz` name is deprecated); requirement is `pymupdf>=1.24.3`.
- Setup notes cover `python3`/`py`, virtual environments and the Chromium download.

## [1.0.1] — 2026-10-19
### Changed
- README, skill description and plugin descriptions now say what Syllabind does: give it a topic and it writes a
  complete course (researched lessons as Markdown), then builds the web, PDF and notes versions. No code changes.

## [1.0.0] — 2026-10-19
### Added
- `syllabind` skill: workflow, writing rules, figure rules, config and verification references.
- Scripts: `new_course.py`, `build.py`, `export.py` (offline HTML, two-pass A4 PDF via Chromium, Markdown notes),
  `annotate.py` (numbered screenshot callouts), `svgkit.py` (diagrams), `verify_html.py`, `check_pdf.py`.
- Web template (light / dark, search, lightbox, progress, mobile) and print stylesheet.
- Sample course (two modules and a syntax appendix) that documents the format.
- Plugin and marketplace manifests, CI on Windows, macOS and Linux, and a skill-zip packaging tool.
- Repository banner, issue and pull request templates, code of conduct and security policy.

[1.0.3]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.3
[1.0.2]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.2
[1.0.1]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.1
[1.0.0]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.0
