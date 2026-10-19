"""Create a new course folder from the bundled example.

usage:  python new_course.py <new-course-dir> --title "My Course 2026" [--with-example-content]

Copies course.yaml, sources.yaml, figures/ and modules/ from the example, sets title and slug, and (unless
--with-example-content) replaces the example modules with two empty starter modules you can fill in.
"""
import argparse
import pathlib
import re
import shutil
import sys

KIT = pathlib.Path(__file__).resolve().parent.parent
EXAMPLE = KIT / "example"

STARTER = """---
id: {id}
title: {title}
level: {level}
duration_min: 15
objectives:
  - First thing the learner can do after this module
  - Second thing
  - Third thing
  - Fourth thing
---

!!! facts "At a glance"
    - **Number** short fact
    - **Number** short fact
    - **Number** short fact
    - **Number** short fact

## {n}.1 First section

Write short paragraphs, tables and figures here.

!!! summary "In one screen"
    - Key point one.
    - Key point two.

## Self-check

<details><summary>Q1. A question the learner should be able to answer?</summary>
The answer.
</details>

## Sources

- Where every fact in this module comes from
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dest")
    ap.add_argument("--title", required=True)
    ap.add_argument("--with-example-content", action="store_true")
    a = ap.parse_args()
    dest = pathlib.Path(a.dest).resolve()
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f"{dest} is not empty")
    shutil.copytree(EXAMPLE, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns("build", "__pycache__", "out"))
    slug = re.sub(r"[^a-z0-9]+", "-", a.title.lower()).strip("-")
    cfg = (dest / "course.yaml").read_text(encoding="utf-8")
    cfg = re.sub(r"(?m)^title: .*$", f'title: "{a.title}"', cfg, count=1)
    cfg = re.sub(r"(?m)^slug: .*$", f"slug: {slug}", cfg, count=1)
    (dest / "course.yaml").write_text(cfg, encoding="utf-8")
    if not a.with_example_content:
        for f in (dest / "modules").glob("*.md"):
            f.unlink()
        level = re.search(r"(?m)^  - name: (.+)$", cfg).group(1).strip().strip('"')
        (dest / "modules" / "M00-introduction.md").write_text(STARTER.format(id="M00", title="Introduction", level=level, n=0), encoding="utf-8")
        (dest / "modules" / "M01-first-topic.md").write_text(STARTER.format(id="M01", title="First topic", level=level, n=1), encoding="utf-8")
    print(f"created {dest}\nnext:  edit course.yaml and modules/, then\n"
          f"  python {KIT / 'scripts' / 'build.py'} \"{dest}\"\n"
          f"  python {KIT / 'scripts' / 'export.py'} \"{dest}\" --dest \"{dest / 'out'}\"")


if __name__ == "__main__":
    main()
