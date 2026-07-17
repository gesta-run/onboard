# Gesta Onboard Artifacts

This directory is published by GitHub Pages.

```sh
curl -fsSL https://artifacts.gesta.run/gesta/install-agent.sh | bash -s -- \
  --control-url https://console.gesta.run \
  --apikey sk-...
```

The default channel is `rc`. Set `GESTA_AGENT_CHANNEL=stable` to use the stable
channel after it is published.

The public installer selects its explicit channel version from `install-agent.sh`.
Release artifacts remain under `agent/<channel>/<version>/`.
