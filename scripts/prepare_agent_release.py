#!/usr/bin/env python3

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import shutil
import subprocess


SUPPORTED_PLATFORMS = {
    "darwin/amd64",
    "darwin/arm64",
    "linux/amd64",
    "linux/arm64",
    "windows/amd64",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-dir", type=pathlib.Path, required=True)
    parser.add_argument("--artifacts-dir", type=pathlib.Path, required=True)
    parser.add_argument("--channel", choices=("rc", "stable"), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--agent-ref", required=True)
    parser.add_argument("--agent-sha", required=True)
    return parser.parse_args()


def rewrite_installers(target: pathlib.Path, channel: str, version: str) -> None:
    base_url = f"https://artifacts.gesta.run/gesta/agent/{channel}/{version}"
    shell_path = target / "install.sh"
    shell_text = shell_path.read_text()
    shell_text, count = re.subn(
        r"install_base_url=\$\{GESTA_AGENT_INSTALL_BASE_URL:-[^}]+\}",
        "install_base_url=${GESTA_AGENT_INSTALL_BASE_URL:-" + base_url + "}",
        shell_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("could not set shell installer base URL")
    shell_path.write_text(shell_text)

    powershell_path = target / "install-agent.ps1"
    powershell_text = powershell_path.read_text()
    powershell_text, count = re.subn(
        r'\[string\]\$BaseUrl = "[^"]+"',
        f'[string]$BaseUrl = "{base_url}"',
        powershell_text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("could not set PowerShell installer base URL")
    powershell_path.write_text(powershell_text)


def write_release_metadata(
    target: pathlib.Path,
    channel: str,
    version: str,
    agent_ref: str,
    agent_sha: str,
) -> None:
    generated_at = (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    payload = {
        "channel": channel,
        "version": version,
        "agent_ref": agent_ref,
        "agent_sha": agent_sha,
        "generated_at": generated_at,
    }
    (target / "release.json").write_text(json.dumps(payload, indent=2) + "\n")


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(target: pathlib.Path) -> dict[str, str]:
    paths = [
        target / "install.sh",
        target / "install-agent.ps1",
        target / "uninstall.sh",
        target / "uninstall-agent.ps1",
        target / "release.json",
        *sorted((target / "bin").glob("gesta-agent-*")),
    ]
    checksums = {path.relative_to(target).as_posix(): sha256(path) for path in paths}
    content = "".join(f"{digest}  {path}\n" for path, digest in checksums.items())
    (target / "SHA256SUMS").write_text(content)
    return checksums


def platform_from_asset(name: str) -> str:
    normalized = name.removeprefix("gesta-agent-").removesuffix(".exe")
    return normalized.replace("-", "/", 1)


def write_manifest(
    artifacts_dir: pathlib.Path,
    channel: str,
    version: str,
    checksums: dict[str, str],
) -> None:
    base_url = f"https://artifacts.gesta.run/gesta/agent/{channel}/{version}"
    assets = {}
    for path, digest in checksums.items():
        name = pathlib.PurePosixPath(path).name
        if not name.startswith("gesta-agent-"):
            continue
        platform = platform_from_asset(name)
        assets[platform] = {"url": f"{base_url}/bin/{name}", "sha256": digest}
    if set(assets) != SUPPORTED_PLATFORMS:
        raise RuntimeError(f"release assets do not match supported platforms: {assets.keys()}")
    manifest_path = artifacts_dir / "agent" / channel / "manifest.json"
    manifest_path.write_text(
        json.dumps({"channel": channel, "version": version, "assets": assets}, indent=2)
        + "\n"
    )


def update_channel_entrypoints(
    artifacts_dir: pathlib.Path,
    channel: str,
    version: str,
) -> None:
    shell_path = artifacts_dir / "install-agent.sh"
    text = shell_path.read_text()
    text, count = re.subn(
        rf"^{channel}_version=.*$",
        f"{channel}_version={version}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError(f"could not update {channel}_version")
    shell_path.write_text(text)

    powershell_path = artifacts_dir / "install-agent.ps1"
    powershell_text = powershell_path.read_text()
    powershell_text, count = re.subn(
        rf'^\${channel}Version\s*=\s*"[^"]*"$',
        f'${channel}Version = "{version}"',
        powershell_text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise RuntimeError(f"could not update {channel}Version")
    powershell_path.write_text(powershell_text)


def update_uninstall_entrypoints(
    artifacts_dir: pathlib.Path,
    release_target: pathlib.Path,
) -> None:
    shell_path = artifacts_dir / "uninstall-agent.sh"
    shutil.copy2(release_target / "uninstall.sh", shell_path)
    shell_path.chmod(0o755)
    shutil.copy2(
        release_target / "uninstall-agent.ps1",
        artifacts_dir / "uninstall-agent.ps1",
    )


def main() -> None:
    args = parse_args()
    repository_root = pathlib.Path(__file__).resolve().parent.parent
    target = args.artifacts_dir / "agent" / args.channel / args.version
    if target.exists():
        raise RuntimeError(f"release already exists: {args.channel}/{args.version}")
    (target / "bin").mkdir(parents=True)
    shutil.copy2(args.agent_dir / "scripts" / "install.sh", target / "install.sh")
    shutil.copy2(
        args.agent_dir / "scripts" / "install-agent.ps1",
        target / "install-agent.ps1",
    )
    shutil.copy2(args.agent_dir / "scripts" / "uninstall.sh", target / "uninstall.sh")
    shutil.copy2(
        args.agent_dir / "scripts" / "uninstall-agent.ps1",
        target / "uninstall-agent.ps1",
    )
    rewrite_installers(target, args.channel, args.version)
    subprocess.run(
        [
            str(args.agent_dir / "scripts" / "build-agent-binaries.sh"),
            str(target / "bin"),
            args.version,
        ],
        check=True,
    )
    write_release_metadata(
        target,
        args.channel,
        args.version,
        args.agent_ref,
        args.agent_sha,
    )
    (target / "install.sh").chmod(0o755)
    (target / "uninstall.sh").chmod(0o755)
    for binary in (target / "bin").glob("gesta-agent-*"):
        binary.chmod(0o755)
    checksums = write_checksums(target)
    write_manifest(args.artifacts_dir, args.channel, args.version, checksums)
    update_channel_entrypoints(
        args.artifacts_dir,
        args.channel,
        args.version,
    )
    update_uninstall_entrypoints(args.artifacts_dir, target)


if __name__ == "__main__":
    main()
