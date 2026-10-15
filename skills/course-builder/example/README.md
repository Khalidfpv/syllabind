# Sample course

A complete course in the Course Builder format: two modules and a syntax appendix. It documents the format itself.

```bash
python figures/make_figures.py            # optional: regenerate the screenshot and diagrams (needs Playwright)
python ../scripts/build.py .
python ../scripts/export.py . --dest out
```
Open `out/Sample Course 2026.html`. `build/` and `out/` are generated and git-ignored.
