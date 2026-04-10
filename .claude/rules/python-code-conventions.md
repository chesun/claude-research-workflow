# Python Code Conventions

**Scope:** `**/*.py`
**Role:** Secondary language (Stata is primary for analysis)

---

## Virtual Environment (Default)

- **Always use a virtual environment** (`venv` or `conda`) unless the user explicitly says to use global Python
- Create with `python -m venv .venv` at project root
- Activate before installing or running: `source .venv/bin/activate`
- If a `.venv/` or `environment.yml` already exists, use it
- Never install packages globally (`pip install` without an active venv) unless explicitly told to

## When to Use Python

- Machine learning / text classification
- Web scraping or API calls
- Simulation and power analysis (when Stata is awkward)
- Data visualization with matplotlib/seaborn (when Stata graphs insufficient)
- Custom scripting and automation

## Project Setup

- `requirements.txt` or `pyproject.toml` for all dependencies
- Pin versions for reproducibility
- Add `.venv/` to `.gitignore`

## Code Style

- Type hints on function signatures
- Docstrings on public functions (Google style)
- `random.seed()` / `np.random.seed()` / `torch.manual_seed()` set once at top
- No hardcoded absolute paths — use `pathlib.Path` with relative paths or environment variables
- Jupyter notebooks for exploration only — production code in `.py` files

## Testing

- `pytest` for unit tests when applicable
- Seed all random operations for reproducibility
