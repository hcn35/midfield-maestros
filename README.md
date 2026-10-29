# Midfield Maestros
Charts of great midfielders from StatsBomb free open data. Who, which season and match: `settings.yaml`.

**Install** (Python 3.11+): `python3.11 -m venv .venv && .venv/bin/pip install -e '.[dev]'`

**Download** the season once into `data/cache/` (gitignored; a second run downloads nothing):

    .venv/bin/python -m maestros.data --download

**Draw** the charts listed in `settings.yaml` into `out/` (gitignored): `.venv/bin/python -m maestros.charts`

**Run the checks** (offline, using the sample match in `tests/fixtures/`):

    .venv/bin/pytest
