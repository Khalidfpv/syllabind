"""Package the skill folder as a zip for claude.ai (Settings › Capabilities › Skills › Upload) or for manual install.

usage:  python tools/package_skill.py            -> dist/course-builder-<version>.zip

The zip holds one top-level folder `course-builder/` with SKILL.md inside, without generated files
(build/, out/, __pycache__). It fails if SKILL.md frontmatter uses keys that claude.ai rejects or exceeds its limits.
"""
import json
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "course-builder"
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKIP = {"build", "out", "__pycache__", "dist"}


def check_frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("SKILL.md: frontmatter must start on line 1")
    keys = re.findall(r"(?m)^([A-Za-z-]+):", m.group(1))
    bad = set(keys) - ALLOWED
    if bad:
        sys.exit(f"SKILL.md: keys not allowed outside Claude Code: {sorted(bad)}")
    name = re.search(r"(?m)^name: (.+)$", m.group(1)).group(1).strip()
    desc = re.search(r"(?m)^description: (.+)$", m.group(1)).group(1).strip()
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        sys.exit("SKILL.md: name must be lowercase letters, digits and hyphens, max 64")
    if len(desc) > 1024 or "<" in desc:
        sys.exit(f"SKILL.md: description must be <= 1024 chars without XML tags (is {len(desc)})")
    return name, len(desc)


def main():
    name, dlen = check_frontmatter()
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    out = ROOT / "dist" / f"{name}-{version}.zip"
    out.parent.mkdir(exist_ok=True)
    n, size = 0, 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SKILL.rglob("*")):
            rel = f.relative_to(SKILL)
            if f.is_dir() or SKIP & set(rel.parts):
                continue
            z.write(f, pathlib.Path(name) / rel)
            n += 1
            size += f.stat().st_size
    if size > 30 * 1024 * 1024:
        sys.exit(f"skill is {size / 1e6:.1f} MB uncompressed; claude.ai accepts up to 30 MB")
    print(f"{out}  ({n} files, {size / 1e6:.2f} MB uncompressed, description {dlen} chars)")


if __name__ == "__main__":
    main()
