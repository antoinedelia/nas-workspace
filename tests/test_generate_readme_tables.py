import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import generate_readme_tables as gen


@pytest.mark.parametrize(
    ("image", "expected"),
    [
        ("ghcr.io/advplyr/audiobookshelf:2.37.1", "ghcr.io/advplyr/audiobookshelf"),
        ("postgres:16.15-alpine", "postgres"),
        ("localhost:5000/app:1.0", "localhost:5000/app"),
        ("localhost:5000/app", "localhost:5000/app"),
        ("app:1.0@sha256:abc", "app"),
    ],
)
def test_strip_tag(image, expected):
    # Arrange / Act
    result = gen.strip_tag(image)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("port", "expected"),
    [
        ("8080:80", "8080"),
        ("8388:8388/udp", "8388"),
        ("127.0.0.1:8080:80", "8080"),
        (3000, None),
        ("80", None),
        ({"published": 8096, "target": 8096}, "8096"),
    ],
)
def test_host_port(port, expected):
    # Arrange / Act
    result = gen.host_port(port)

    # Assert
    assert result == expected


def test_describe_stack_collects_images_ports_and_variables(tmp_path):
    # Arrange
    stack = tmp_path / "app"
    stack.mkdir()
    (stack / "compose.yaml").write_text(
        "services:\n"
        "  db:\n"
        "    image: postgres:15.19\n"
        "    environment:\n"
        "      - POSTGRES_PASSWORD=${DB_PASSWORD}\n"
        "    healthcheck:\n"
        '      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER"]\n'
        "  web:\n"
        "    image: example/web:1.0\n"
        "    ports:\n"
        "      - 3002:3000\n"
        "    environment:\n"
        "      - SECRET=${JWT_SECRET:-default}\n"
    )
    (stack / ".env.example").write_text("# comment\nEXTRA=CHANGEME\n")

    # Act
    row = gen.describe_stack(stack)

    # Assert
    assert row["stack"] == "`app`"
    assert row["images"] == "`postgres`<br>`example/web`"
    assert row["ports"] == "3002"
    assert row["variables"] == "`DB_PASSWORD`, `EXTRA`, `JWT_SECRET`"


def test_describe_stack_reports_vpn_network_mode_and_env_file(tmp_path):
    # Arrange
    stack = tmp_path / "vpn-app"
    stack.mkdir()
    (stack / "compose.yaml").write_text(
        "services:\n  app:\n    image: example/app:1.0\n    network_mode: container:gluetun\n    env_file:\n      - .env\n"
    )

    # Act
    row = gen.describe_stack(stack)

    # Assert
    assert row["ports"] == "via gluetun"
    assert row["variables"] == "`.env` file"


def test_replace_section_swaps_only_the_marked_content():
    # Arrange
    readme = f"before\n{gen.START_MARKER}\nold\n{gen.END_MARKER}\nafter\n"

    # Act
    result = gen.replace_section(readme, "new")

    # Assert
    assert result == f"before\n{gen.START_MARKER}\nnew\n{gen.END_MARKER}\nafter\n"


def test_replace_section_requires_markers():
    # Arrange / Act / Assert
    with pytest.raises(SystemExit):
        gen.replace_section("no markers here", "table")


def test_describe_stack_ignores_default_bridge_network_mode(tmp_path):
    # Arrange
    stack = tmp_path / "bridged"
    stack.mkdir()
    (stack / "compose.yaml").write_text(
        "services:\n  app:\n    image: example/app:1.0\n    network_mode: bridge\n    ports:\n      - 8008:8000/tcp\n"
    )

    # Act
    row = gen.describe_stack(stack)

    # Assert
    assert row["ports"] == "8008"
