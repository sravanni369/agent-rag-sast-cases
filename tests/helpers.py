import importlib.util
from pathlib import Path

CASES = Path(__file__).resolve().parent.parent / "cases"


def load(case, variant, filename="app.py"):
    """Fresh module per call, so one test's side effects never reach another."""
    path = CASES / case / variant / filename
    spec = importlib.util.spec_from_file_location(f"{case}_{variant}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
