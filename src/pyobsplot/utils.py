"""
Utility methods and variables 
"""

import pathlib
import shutil
import subprocess

# Output directory of esbuild
bundler_output_dir = pathlib.Path(__file__).parent / "static"
# Default renderer
default_renderer = "widget"
available_renderers = ["widget", "jsdom"]


# Code below taken from altair_saver :
# https://github.com/altair-viz/altair_saver/blob/master/altair_saver/savers/_node.py


def npm_bin(global_: bool) -> str:
    """Locate the npm binary directory."""
    npm = shutil.which("npm")
    if not npm:
        raise RuntimeError("npm has not been found.")
    cmd = [npm, "bin"]
    if global_:
        cmd.append("--global")
    p = subprocess.run(
        cmd,
        capture_output=True,
        encoding="Utf8",
    )
    if p.returncode != 0:
        raise RuntimeError(
            f"npm bin error (${p.returncode}): ${p.stderr} - ${p.stdout}"
        )
    # Get script output
    out = p.stdout
    return out.strip()


def exec_path(name: str) -> str:
    """Return the path of the node executable passed as argument."""
    for path in [None, npm_bin(global_=True), npm_bin(global_=False)]:
        exc = shutil.which(name, path=path)
        if exc:
            return exc
    raise RuntimeError(name + " has not been found.")
