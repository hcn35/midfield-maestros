"""Read settings.yaml: which player, team, competition, season and match the page is about."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "settings.yaml"


@dataclass(frozen=True)
class Settings:
    player_id: int
    team: str
    competition_id: int
    season_id: int
    charts: list = field(default_factory=list)
    match_id: int | None = None


def load_settings(path: Path = DEFAULT_PATH) -> Settings:
    raw = yaml.safe_load(Path(path).read_text())
    return Settings(
        player_id=int(raw["player_id"]),
        team=str(raw["team"]),
        competition_id=int(raw["competition_id"]),
        season_id=int(raw["season_id"]),
        charts=list(raw.get("charts") or []),
        match_id=int(raw["match_id"]) if raw.get("match_id") is not None else None,
    )
