"""Friendly setup checks shared by the scripts.

`import _setup` (first import of a script) exits with a one-line instruction when a required Python package is missing.
`launch_chromium(playwright)` does the same when Playwright's Chromium has not been downloaded yet.
"""
import importlib
import pathlib
import sys

REQUIREMENTS = pathlib.Path(__file__).resolve().parent / "requirements.txt"
# import name -> pip name
PACKAGES = {"markdown": "markdown", "yaml": "pyyaml", "PIL": "pillow", "playwright": "playwright", "pymupdf": "pymupdf", "pypdf": "pypdf"}


def check_packages():
    missing = []
    for module, pip_name in PACKAGES.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(pip_name)
    if missing:
        sys.exit(f"Missing Python packages: {', '.join(missing)}\n"
                 f"Install them once with:\n  \"{sys.executable}\" -m pip install -r \"{REQUIREMENTS}\"\n"
                 f"then:\n  \"{sys.executable}\" -m playwright install chromium")


def launch_chromium(playwright):
    try:
        return playwright.chromium.launch()
    except Exception as e:                                  # playwright raises its own Error type
        text = str(e)
        if "Executable doesn't exist" in text or "playwright install" in text:
            sys.exit("Chromium is not installed for Playwright. Run this once, then retry:\n"
                     f"  \"{sys.executable}\" -m playwright install chromium\n"
                     "(on a bare Linux server also: python -m playwright install-deps chromium)")
        raise


check_packages()
