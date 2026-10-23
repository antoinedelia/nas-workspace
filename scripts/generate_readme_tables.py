# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Regenerate the stacks table in README.md from docker-compose/*/compose.yaml.

Usage:
    uv run scripts/generate_readme_tables.py           # rewrite README.md
    uv run scripts/generate_readme_tables.py --check   # exit 1 if README.md is stale
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
COMPOSE_DIR = ROOT / "docker-compose"
START_MARKER = "<!-- stacks:start -->"
END_MARKER = "<!-- stacks:end -->"

# `(?<!\$)` skips `$${VAR}`, which Compose treats as an escaped literal.
VARIABLE_PATTERN = re.compile(r"(?<!\$)\$\{([A-Za-z_][A-Za-z0-9_]*)")


def strip_tag(image: str) -> str:
    """Return the image name without its tag or digest, so Renovate bumps don't change the README."""
    image = image.split("@", 1)[0]
    last_segment = image.rsplit("/", 1)[-1]
    if ":" in last_segment:
        image = image.rsplit(":", 1)[0]
    return image


def host_port(port: str | int | dict) -> str | None:
    """Return the host side of a Compose port mapping, or None if the host port is not fixed."""
    if isinstance(port, dict):
        published = port.get("published")
        return str(published) if published else None
    parts = str(port).split("/", 1)[0].split(":")
    if len(parts) == 1:
        return None
    return parts[-2]


def parse_env_example_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()
    keys = set()
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0].strip())
    return keys


def describe_stack(stack_dir: Path) -> dict[str, str]:
    data = yaml.safe_load((stack_dir / "compose.yaml").read_text())
    services = data.get("services") or {}

    images = []
    ports: set[str] = set()
    network_modes: set[str] = set()
    uses_env_file = False
    for service in services.values():
        if "image" in service:
            images.append(strip_tag(service["image"]))
        for port in service.get("ports", []):
            published = host_port(port)
            if published:
                ports.add(published)
        mode = service.get("network_mode", "")
        if mode.startswith("container:"):
            network_modes.add(f"via {mode.split(':', 1)[1]}")
        elif mode and mode != "bridge":
            network_modes.add(mode)
        uses_env_file = uses_env_file or "env_file" in service

    variables = set(VARIABLE_PATTERN.findall(json.dumps(data)))
    variables |= parse_env_example_keys(stack_dir / ".env.example")

    ports_cell = ", ".join(sorted(ports, key=int)) if ports else ""
    if network_modes:
        ports_cell = ", ".join(filter(None, [ports_cell, *sorted(network_modes)]))

    variables_cell = ", ".join(f"`{name}`" for name in sorted(variables))
    if uses_env_file:
        variables_cell = ", ".join(filter(None, [variables_cell, "`.env` file"]))

    return {
        "stack": f"`{stack_dir.name}`",
        "images": "<br>".join(f"`{image}`" for image in images),
        "ports": ports_cell or "-",
        "variables": variables_cell or "-",
    }


def render_table() -> str:
    rows = [describe_stack(path.parent) for path in sorted(COMPOSE_DIR.glob("*/compose.yaml"))]
    lines = [
        "| Stack | Image(s) | Host ports | Variables to set in Komodo |",
        "| --- | --- | --- | --- |",
    ]
    lines += [f"| {row['stack']} | {row['images']} | {row['ports']} | {row['variables']} |" for row in rows]
    return "\n".join(lines)


def replace_section(readme: str, table: str) -> str:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise SystemExit(f"README.md must contain {START_MARKER} and {END_MARKER}")
    return f"{readme[: start + len(START_MARKER)]}\n{table}\n{readme[end:]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if README.md is out of date instead of rewriting it")
    args = parser.parse_args()

    current = README.read_text()
    updated = replace_section(current, render_table())
    if updated == current:
        return 0
    if args.check:
        print("README.md is out of date. Run: uv run scripts/generate_readme_tables.py", file=sys.stderr)
        return 1
    README.write_text(updated)
    print("README.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
