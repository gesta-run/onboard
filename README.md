# Gesta Onboard

User-oriented installation scripts and release assets for Gesta.

Source code for the Gesta agent lives in the private `gesta-run/gesta-agent`
repository. This repository only hosts installable artifacts for onboarding
users and machines.

## Install Agent

```sh
cd "${HOME:-/tmp}" && curl -fsSL https://artifacts.gesta.run/gesta/install-agent.sh | bash -s -- \
  --control-url https://console.gesta.run \
  --apikey sk-...
```

The production installer selects the `stable` channel. It becomes installable
after the first stable agent artifact is published.

For preproduction, use the RC installer:

```sh
cd "${HOME:-/tmp}" && curl -fsSL https://artifacts.gesta.run/gesta/install-agent-rc.sh | bash -s -- \
  --control-url https://pre-api.gesta.run \
  --apikey sk-...
```

## Layout

- `artifacts/install-agent.sh`: production entrypoint for the stable channel.
- `artifacts/install-agent-rc.sh`: preproduction entrypoint for the RC channel.
- `artifacts/agent/<channel>/<version>/`: immutable release installers and binaries.
- `artifacts/agent/<channel>/manifest.json`: mutable channel pointer consumed by
  the Control Plane for automatic upgrades. It contains the target version and
  SHA256 for each supported platform.

GitHub Pages publishes the `artifacts/` directory.
