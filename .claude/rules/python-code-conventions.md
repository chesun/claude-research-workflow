# Python Code Conventions

**Scope:** `**/*.py`
**Role:** Secondary language (Stata is primary for analysis)

---

## When to Use Python

- oTree experiment code
- Custom Qualtrics JS/HTML generation scripts
- Machine learning / text classification
- Web scraping or API calls
- Simulation and power analysis (when Stata is awkward)
- Data visualization with matplotlib/seaborn (when Stata graphs insufficient)

## Virtual Environment (Default)

- **Always use a virtual environment** (`venv` or `conda`) unless the user explicitly says global
- Create with `python -m venv .venv`
- Activate before installing or running: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows)
- If `.venv/` or `environment.yml` already exists in the project, use it
- **Never install packages globally** (`pip install` without an active venv) without explicit user instruction
- Add `.venv/` to `.gitignore`

## Project Setup

- `requirements.txt` or `pyproject.toml` for all dependencies
- Pin versions for reproducibility

## Code Style

- Type hints on function signatures
- Docstrings on public functions (Google style)
- `random.seed()` / `np.random.seed()` / `torch.manual_seed()` set once at top
- No hardcoded absolute paths — use `pathlib.Path` with relative paths or environment variables
- Jupyter notebooks for exploration only — production code in `.py` files

## oTree Specifics

- Follow oTree 5.x patterns (not legacy oTree 3.x)
- Models in `__init__.py`, pages as classes
- Use `live_method` for real-time interactions
- Session configs in `settings.py`

## Testing

- `pytest` for unit tests when applicable
- Seed all random operations for reproducibility
