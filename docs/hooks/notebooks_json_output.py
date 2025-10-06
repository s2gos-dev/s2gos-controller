import json, html
from pathlib import Path
import shutil
import nbformat as nbf

def _patch_notebook(path: Path):
    nb = nbf.read(path, as_version=4)
    changed = False
    for cell in nb.cells:
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            if isinstance(data, dict) and "application/json" in data:
                pretty = html.escape(json.dumps(data["application/json"],
                                                indent=2,
                                                ensure_ascii=False))
                data["text/html"] = f"<pre><code class='text-json'>{pretty}</code></pre>"
                changed = True
    if changed:
        nbf.write(nb, path)
    return changed

def _update_files_in_docs(source: Path, destination: Path):
    shutil.copytree(source, destination, dirs_exist_ok=True)

# This hook (1) updates the notebooks with each `mkdocs serve`
# or `mkdocs build` and (2) changes the output type of notebook cells from
# `json/application` to `text/html` to make the output readable.
def on_pre_build(config, **kwargs):
    source = Path.cwd() / "notebooks"
    destination = Path.cwd() / "docs/notebooks"

    _update_files_in_docs(source, destination)
    print(f"[hooks] Updated notebooks: {source} to {destination}")

    for ipynb in destination.rglob("*.ipynb"):
        if _patch_notebook(ipynb):
            print(f"[hooks] Patched: {ipynb}")
