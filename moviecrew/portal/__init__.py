"""FastAPI portal for MovieCrew — the PLAN path only (concept -> Project JSON).

Optional subpackage: requires the `portal` extra (fastapi + uvicorn). Nothing
in moviecrew's core import path (moviecrew/__init__.py, cli.py, crew.py, ...)
imports this package, so the CLI and core tests run without fastapi installed.
"""
