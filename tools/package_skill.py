"""Package the skill folder as a zip for claude.ai (Settings › Capabilities › Skills › Upload) or for manual install.

usage:  python tools/package_skill.py            -> dist/syllabind-<version>.zip

The zip holds one top-level folder `syllabind/` with SKILL.md inside, without generated files
(build/, out/, __pycache__). It fails if SKILL.md frontmatter uses keys that claude.ai rejects or exceeds its limits.
"""
import json
import pathlib
import re
import sys
import zipfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "syllabind"
ALLOWED = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
SKIP = {"build", "out", "__pycache__", "dist"}


def check_frontmatter():
    """Parse SKILL.md frontmatter with a real YAML parser (a stray ': ' in the description breaks loading) and check limits."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("SKILL.md: frontmatter must start on line 1 and end with ---")
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        sys.exit(f"SKILL.md: frontmatter is not valid YAML: {e}")
    if not isinstance(fm, dict):
        sys.exit("SKILL.md: frontmatter must be a YAML mapping")
    bad = set(fm) - ALLOWED
    if bad:
        sys.exit(f"SKILL.md: keys not allowed outside Claude Code: {sorted(bad)}")
    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        sys.exit("SKILL.md: name must be lowercase letters, digits and hyphens, max 64")
    if not isinstance(desc, str) or not desc.strip():
        sys.exit("SKILL.md: description is missing or not a string")
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
