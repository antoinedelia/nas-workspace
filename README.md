# NAS Workspace

Repository holding the configuration of all my Docker Compose stacks, deployed with [Komodo](https://komo.do/), updated with [Renovate](https://docs.renovatebot.com/).

## How it works

Renovate will automatically look for new Docker image versions and open a PR. Once approved and merged, it will trigger Komodo, and replace the Docker image of said app to its newer version.

## Stacks

Generated from `docker-compose/*/compose.yaml` by `scripts/generate_readme_tables.py`; do not edit by hand. A GitHub Action refreshes it on pull requests, or run `uv run scripts/generate_readme_tables.py` locally.

<!-- stacks:start -->
| Stack | Image(s) | Host ports | Variables to set in Komodo |
| --- | --- | --- | --- |
| `audiobookshelf` | `ghcr.io/advplyr/audiobookshelf` | 13378 | - |
| `bazarr` | `ghcr.io/linuxserver/bazarr` | 6767 | - |
| `beszel` | `henrygd/beszel`<br>`henrygd/beszel-agent` | 8090, host | `KEY` |
| `changedetection` | `ghcr.io/dgtlmoon/changedetection.io` | 5050 | - |
| `cross-seed` | `ghcr.io/cross-seed/cross-seed` | 2468 | - |
| `cyberchef` | `ghcr.io/gchq/cyberchef` | 4564 | - |
| `ddns-updater` | `qmcgaw/ddns-updater` | 8008 | `SHOUTRRR_ADDRESSES` |
| `filebrowser-quantum` | `gtstef/filebrowser` | 8147 | - |
| `flaresolverr` | `ghcr.io/flaresolverr/flaresolverr` | 8191 | - |
| `glance` | `glanceapp/glance` | 6699 | - |
| `gluetun` | `qmcgaw/gluetun` | 1613, 5030, 5031, 5812, 6881, 8080, 8388, 8888, 50300 | `OPENVPN_PASSWORD`, `OPENVPN_USER` |
| `homepage` | `ghcr.io/gethomepage/homepage` | 3000 | - |
| `jellyfin` | `lscr.io/linuxserver/jellyfin` | 8096 | - |
| `jellystat` | `postgres`<br>`cyfershepard/jellystat` | 3002 | `JWT_SECRET`, `POSTGRES_PASSWORD`, `POSTGRES_USER` |
| `joplin` | `postgres`<br>`joplin/server` | 5433, 22300 | `MAILER_AUTH_PASSWORD`, `MAILER_AUTH_USER`, `MAILER_NOREPLY_EMAIL`, `POSTGRES_DATABASE`, `POSTGRES_DB`, `POSTGRES_PASSWORD`, `POSTGRES_USER` |
| `komga` | `gotson/komga` | 25600 | - |
| `lidarr` | `ghcr.io/linuxserver/lidarr` | 8686 | - |
| `lubelog` | `ghcr.io/hargata/lubelogger` | 1996 | - |
| `metube` | `ghcr.io/alexta69/metube` | 8081 | - |
| `nametag` | `postgres`<br>`ghcr.io/mattogodoy/nametag`<br>`alpine` | 3001 | `CRON_SECRET`, `DB_NAME`, `DB_PASSWORD`, `DB_USER`, `.env` file |
| `navidrome` | `deluan/navidrome` | 4533 | - |
| `netalertx` | `ghcr.io/jokob-sk/netalertx` | host | - |
| `nginx-proxy-manager` | `jc21/nginx-proxy-manager` | 81, 8341, 8766 | - |
| `prowlarr` | `lscr.io/linuxserver/prowlarr` | 9797 | - |
| `qbittorrent` | `lscr.io/linuxserver/qbittorrent` | via gluetun | - |
| `radarr` | `ghcr.io/linuxserver/radarr` | 7878 | - |
| `seerr` | `ghcr.io/seerr-team/seerr` | 5055 | - |
| `sonarr` | `ghcr.io/linuxserver/sonarr` | 8989 | - |
| `soulseek` | `slskd/slskd` | via gluetun | `SLSKD_VPN_GLUETUN_API_KEY`, `SLSKD_VPN_GLUETUN_URL` |
| `stirling-pdf` | `frooodle/s-pdf` | 1646 | - |
<!-- stacks:end -->

## Upgrading Komodo

To upgrade Komodo, find the [latest Komodo release](https://github.com/moghtech/komodo/releases).

Then, following the [official setup Komodo documentation](https://komo.do/docs/setup/ferretdb), edit the `.env` file with the new image version.

Finally, run `sudo docker compose -p komodo -f docker-compose.yml --env-file .env up -d` to upgrade Komodo.

## Resources

* https://docs.renovatebot.com/configuration-options/
* https://nickcunningh.am/blog/how-to-automate-version-updates-for-your-self-hosted-docker-containers-with-gitea-renovate-and-komodo
