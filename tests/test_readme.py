from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"


def test_readme_is_under_15_lines():
    assert len(README.read_text().splitlines()) < 15
