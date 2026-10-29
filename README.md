# Midfield Maestros
Charts of great midfielders from StatsBomb free open data. Who and which season: `settings.yaml`.

**Install** (Python 3.11+):

    python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'

**Download** the season once into `data/cache/` (gitignored; a second run downloads nothing):

    .venv/bin/python -m maestros.data --download

**Run the checks** (offline, using the sample match in `tests/fixtures/`):

    .venv/bin/pytest
