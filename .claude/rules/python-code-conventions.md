---
paths:
  - "**/*.py"
---

# Python Code Conventions

**Scope:** `**/*.py`
**Role:** Secondary language (Stata is primary for analysis)

---

## Virtual Environment (Default)

**New Python analysis runs in the project's own virtual environment, never the system Python.** One environment per project, so one project's upgrades cannot break another's results.

- **Before the first script in a project:**
  - look for `.venv/` (or `environment.yml` for conda) at the project root, and use it if present;
  - if there is none, create one: `py -m venv .venv` on Windows, `python3 -m venv .venv` on macOS/Linux;
  - add `.venv/` to `.gitignore`.
- **Run and install through the environment's own interpreter,** not an activated shell. Activation does not carry over between tool calls.
  - Windows: `.venv\Scripts\python.exe script.py` and `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
  - macOS/Linux: `.venv/bin/python script.py` and `.venv/bin/python -m pip install -r requirements.txt`.
- **Pin what you install.** Every package the analysis imports goes in `requirements.txt` with its exact version (`package==1.2.3`; read it from `pip freeze`), in the same change that first uses it. A fresh `.venv` plus `pip install -r requirements.txt` must reproduce the environment.
- **Never install globally:** no `pip install` outside the environment, and no `pip install --user`, unless the user explicitly says so.
- **Exception: the workflow's own tools.** Scripts under `bin/` and `.claude/hooks/` are stdlib-only by design and run with the system interpreter (`py -I` / `python3 -I`). They must never import a third-party package. If one needs one, it moves to a project environment.

## When to Use Python

- Machine learning / text classification
- Web scraping or API calls
- Simulation and power analysis (when Stata is awkward)
- Data visualization with matplotlib/seaborn (when Stata graphs insufficient)
- Custom scripting and automation

## Project Setup

- `requirements.txt` (or `pyproject.toml`) lists every dependency, pinned to an exact version (see above).
- Record the Python version too, e.g. in a comment at the top of `requirements.txt`, because an environment built on another minor version can resolve differently.

## Code Style

- Type hints on function signatures
- Docstrings on public functions (Google style)
- `random.seed()` / `np.random.seed()` / `torch.manual_seed()` set once at top
- No hardcoded absolute paths — use `pathlib.Path` with relative paths or environment variables
- Jupyter notebooks for exploration only — production code in `.py` files

## Testing

- `pytest` for unit tests when applicable
- Seed all random operations for reproducibility
