# NAS Workspace

Repository holding the configuration of all my Docker Compose stacks, deployed with [Komodo](https://komo.do/), updated with [Renovate](https://docs.renovatebot.com/).

## How it works

Renovate will automatically look for new Docker image versions and open a PR. Once approved and merged, it will trigger Komodo, and replace the Docker image of said app to its newer version.

## Upgrading Komodo

To upgrade Komodo, find the [latest Komodo release](https://github.com/moghtech/komodo/releases).

Then, following the [official setup Komodo documentation](https://komo.do/docs/setup/ferretdb), edit the `.env` file with the new image version.

Finally, run `sudo docker compose -p komodo -f docker-compose.yml --env-file .env up -d` to upgrade Komodo.

## Resources

* https://docs.renovatebot.com/configuration-options/
* https://nickcunningh.am/blog/how-to-automate-version-updates-for-your-self-hosted-docker-containers-with-gitea-renovate-and-komodo
