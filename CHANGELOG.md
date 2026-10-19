# Changelog

All notable changes are listed here. Versions follow [Semantic Versioning](https://semver.org/).

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

[1.0.1]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.1
[1.0.0]: https://github.com/Khalidfpv/syllabind/releases/tag/v1.0.0
