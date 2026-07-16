# Gesta Onboard

User-oriented installation scripts and release assets for Gesta.

Source code for the Gesta agent lives in the private `gesta-run/gesta-agent`
repository. This repository only hosts installable artifacts for onboarding
users and machines.

## Install Agent

```sh
cd "${HOME:-/tmp}" && curl -fsSL https://gesta-run.github.io/onboard/install-agent.sh | bash -s -- \
  --control-url https://console.gesta.run \
  --apikey sk-...
```

The public installer uses the `rc` channel by default. Set
`GESTA_AGENT_CHANNEL=stable` to install the stable channel after a stable agent
artifact has been published.

## Layout

- `artifacts/install-agent.sh`: public entrypoint for agent installation.
- `artifacts/install-agent.sh`: explicit current version for each channel.
- `artifacts/agent/rc/<version>/`: immutable release candidate installer and binaries.
- `artifacts/agent/stable/<version>/`: immutable stable installer and binaries.

GitHub Pages publishes the `artifacts/` directory.
