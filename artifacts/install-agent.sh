#!/bin/sh
set -eu

ensure_stable_cwd() {
  if pwd >/dev/null 2>&1; then
    return
  fi
  if [ -n "${HOME:-}" ] && [ -d "$HOME" ] && cd "$HOME" 2>/dev/null; then
    return
  fi
  cd /tmp 2>/dev/null || cd /
}

ensure_stable_cwd

channel=${GESTA_AGENT_CHANNEL:-rc}
rc_version=0.0.1-rc50
stable_version=

case "$channel" in
  rc|stable)
    ;;
  *)
    printf 'unsupported GESTA_AGENT_CHANNEL: %s\n' "$channel" >&2
    printf 'supported channels: rc, stable\n' >&2
    exit 2
    ;;
esac

case "$channel" in
  rc) version=$rc_version ;;
  stable) version=$stable_version ;;
esac
if [ -z "$version" ]; then
  printf 'no %s agent release is published\n' "$channel" >&2
  exit 1
fi
if ! printf '%s\n' "$version" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$'; then
  printf 'invalid %s agent release version: %s\n' "$channel" "$version" >&2
  exit 1
fi

channel_url=${GESTA_AGENT_INSTALL_BASE_URL:-https://artifacts.gesta.run/gesta/agent/$channel}
install_tmp=${TMPDIR:-/tmp}/gesta-install-agent.$$

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

base_url="$channel_url/$version"
install_url=$base_url/install.sh
download "$install_url" "$install_tmp"

chmod +x "$install_tmp"
GESTA_AGENT_INSTALL_BASE_URL=$base_url exec /bin/sh "$install_tmp" "$@"
