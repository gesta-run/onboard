#!/bin/sh
set -eu

entrypoint_url=${GESTA_AGENT_INSTALLER_ENTRYPOINT_URL:-https://artifacts.gesta.run/gesta/install-agent.sh}
install_tmp=${TMPDIR:-/tmp}/gesta-install-agent-rc.$$

cleanup() {
  rm -f "$install_tmp"
}
trap cleanup EXIT INT TERM

download() {
  url=$1
  output=$2
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$url" -o "$output"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$output" "$url"
  else
    printf 'curl or wget is required\n' >&2
    exit 2
  fi
}

download "$entrypoint_url" "$install_tmp"
GESTA_AGENT_CHANNEL=rc exec /bin/sh "$install_tmp" "$@"
