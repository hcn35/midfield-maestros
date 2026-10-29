"""Draw the charts named in settings.yaml into out/, from the cached match data.

    python -m maestros.charts
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # files only, no window

import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch

from maestros.data import CACHE_DIR, load_events, matches_path, player_events
from maestros.settings import ROOT, Settings, load_settings

OUT_DIR = ROOT / "out"
COMPLETED = "#1f77b4"
INCOMPLETE = "#d62728"


def pass_map(events: list[dict], player_id: int, match: dict):
    """A vertical pitch with one arrow per pass by the player, start to end location."""
    passes = [e for e in player_events(events, player_id) if e["type"]["name"] == "Pass"]
    done = [p for p in passes if "outcome" not in p["pass"]]
    missed = [p for p in passes if "outcome" in p["pass"]]

    pitch = VerticalPitch(pitch_type="statsbomb", line_zorder=1)
    fig, ax = pitch.draw(figsize=(7.2, 10.4))
    for group, colour, name in ((done, COMPLETED, "Completed"), (missed, INCOMPLETE, "Incomplete")):
        pitch.arrows(
            [p["location"][0] for p in group],
            [p["location"][1] for p in group],
            [p["pass"]["end_location"][0] for p in group],
            [p["pass"]["end_location"][1] for p in group],
            ax=ax, color=colour, width=2, headwidth=5, headlength=5,
            label=f"{name} ({len(group)})",
        )
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False, fontsize=12)

    player = passes[0]["player"]["name"] if passes else f"Player {player_id}"
    home = match["home_team"]["home_team_name"]
    away = match["away_team"]["away_team_name"]
    fig.suptitle(f"{player} passes\n{home} v {away} · {match['match_date']}", fontsize=14)
    return fig


CHARTS = ("pass_map",)  # names allowed in settings.yaml charts


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _match(settings: Settings, cache_dir: Path) -> dict:
    if settings.match_id is None:
        raise SystemExit("settings.yaml needs a match_id for these charts")
    path = matches_path(settings, cache_dir)
    if not path.exists():
        raise SystemExit(f"No cached matches at {path}. Run: python -m maestros.data --download")
    for match in json.loads(path.read_text()):
        if match["match_id"] == settings.match_id:
            return match
    raise SystemExit(f"match_id {settings.match_id} is not a cached {settings.team} match")


def build(settings: Settings, cache_dir: Path = CACHE_DIR, out_dir: Path = OUT_DIR) -> list[Path]:
    """Draw every chart in settings.charts. Returns the files written."""
    unknown = [c for c in settings.charts if c not in CHARTS]
    if unknown:
        raise SystemExit(f"Unknown chart(s) in settings.yaml: {', '.join(unknown)}")
    match = _match(settings, Path(cache_dir))
    events = load_events(settings.match_id, cache_dir)
    written = []
    for name in settings.charts:
        path = Path(out_dir) / f"{name}.png"
        save(globals()[name](events, settings.player_id, match), path)
        written.append(path)
    return written


def main() -> None:
    for path in build(load_settings()):
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
