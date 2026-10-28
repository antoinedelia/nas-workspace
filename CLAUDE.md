# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Configuration-only repo holding Docker Compose stacks for a NAS. There is no build or lint step. The only code is a README generator (see Commands). Deployment is GitOps: [Renovate](https://docs.renovatebot.com/) opens PRs bumping image tags, and merging to `main` triggers [Komodo](https://komo.do/) to redeploy the changed stack. Commits like `chore(deps): update <image> to vX` are Renovate-generated and squash-merged (`(#NNN)`).

## Commands

```sh
uv run scripts/generate_readme_tables.py           # rewrite the README stacks table
uv run scripts/generate_readme_tables.py --check   # exit 1 if it is stale
uv run --with pytest --with pyyaml python -m pytest tests
uv run --with pytest --with pyyaml python -m pytest tests -k describe_stack   # single test

# validate a stack (stacks with env_file need a .env present; Komodo provides it in production)
docker compose -f docker-compose/<app>/compose.yaml config -q
```

## Layout

- `docker-compose/<app>/compose.yaml`: one stack per app, one directory per app. Some older files still carry the obsolete `version:` key. Omit it in new files.
  About half the compose files use CRLF line endings. Preserve them when editing (a Python read/write round-trip silently converts them to LF).
- `renovate.json`: per-package rules. When adding an image that needs special handling, add a rule here. Existing rules:
  - strict `semver` versioning for the linuxserver qbittorrent and lidarr images
  - `beszel` and `beszel-agent` grouped into a single PR
  - `minimumReleaseAge: 1 day` on all docker updates
  - patch updates automerge for metube, glance and homepage only (as PRs)
  - postgres pinned (updates disabled) in `joplin`, which needs an old version
- `scripts/generate_readme_tables.py`: regenerates the stacks table in `README.md` (image names without tags, host ports, variables to set in Komodo). Tests are in `tests/`.
- `.github/workflows/readme.yaml`: on PRs that touch `docker-compose/**`, runs the tests, regenerates the table, and pushes a commit to the PR branch if it changed. Never edit the table between the `stacks:start` and `stacks:end` markers by hand.
- Komodo itself is not in this repo. Its upgrade procedure is in `README.md`.

## Conventions

- **Pin images to explicit version tags**, never `latest`. Renovate can only bump pinned tags.
- Persistent data is bind-mounted from the NAS: app config under `/volume2/dockerssd/<app>`, media/data under `/volume1/data`. Named volumes are the exception (only nametag's Postgres uses one).
- `restart: unless-stopped` on every service.
- Postgres services have a `pg_isready` healthcheck, and the apps use `depends_on: condition: service_healthy`.
- Linuxserver-style containers use `PUID=1026`, `PGID=100`, `TZ=Europe/Paris`.
- Secrets are referenced as `${VAR}` in compose files and supplied by Komodo. Do not hardcode secrets. `.env` is gitignored. To document required variables, commit a `.env.example` with `CHANGEME` placeholders (see `docker-compose/jellystat/.env.example`). The generator reads it.

## VPN network topology (cross-file dependency)

`gluetun` is the VPN gateway (Private Internet Access, with port forwarding). `qbittorrent` and `soulseek` use `network_mode: container:gluetun`, so they have no ports of their own.

- Their ports are published on the **gluetun** service (8080/6881 for qbittorrent, 5030/5031/50300 for soulseek, etc.). A new VPN-routed app needs its ports added to `gluetun/compose.yaml`.
- Gluetun's `VPN_PORT_FORWARDING_UP_COMMAND` and `VPN_PORT_FORWARDING_DOWN_COMMAND` call the qBittorrent WebUI API at `127.0.0.1:8080` to set the forwarded port. If you change qBittorrent's `WEBUI_PORT`, update these commands too.
- Gluetun must be running before the VPN-routed containers start. Restarting gluetun requires restarting them.
