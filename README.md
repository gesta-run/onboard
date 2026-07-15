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

## Layout

- `docs/install-agent.sh`: public entrypoint for agent installation.
- `docs/agent/install.sh`: installer mirrored under the agent asset root.
- `docs/agent/bin/`: published platform binaries.
- `docs/agent/SHA256SUMS`: checksums for the installer and binaries.

GitHub Pages serves this repository from `docs/`.
