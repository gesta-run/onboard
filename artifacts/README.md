# Gesta Onboard Artifacts

This directory is published by GitHub Pages.

```sh
curl -fsSL https://artifacts.gesta.run/gesta/install-agent.sh | bash -s -- \
  --control-url https://console.gesta.run \
  --apikey sk-...
```

`install-agent.sh` selects the stable channel for production use. It becomes
installable after the first stable release is published.

For preproduction, use `install-agent-rc.sh`; it always selects the RC channel.
Both entrypoints resolve immutable releases under `agent/<channel>/<version>/`.

The latest published release also provides confirmation-based uninstall
entrypoints for macOS/Linux and Windows:

```sh
curl -fsSL https://artifacts.gesta.run/gesta/uninstall-agent.sh | sh
```

```powershell
irm https://artifacts.gesta.run/gesta/uninstall-agent.ps1 | iex
```

Download the script before running it when passing `--keep-data`/`--yes` on
macOS/Linux or `-KeepData`/`-Yes` on Windows.
