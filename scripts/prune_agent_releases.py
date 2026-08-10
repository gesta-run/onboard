#!/usr/bin/env python3

import argparse
import json
import pathlib
import re
import shutil


RC_VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)-rc(\d+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=pathlib.Path, required=True)
    parser.add_argument("--keep", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def rc_version_key(version: str) -> tuple[int, int, int, int]:
    match = RC_VERSION_PATTERN.fullmatch(version)
    if match is None:
        raise ValueError(f"invalid RC release directory: {version}")
    return tuple(int(part) for part in match.groups())


def releases_to_prune(channel_dir: pathlib.Path, keep: int) -> list[pathlib.Path]:
    if keep < 1:
        raise ValueError("keep must be at least 1")
    if not channel_dir.is_dir():
        raise RuntimeError(f"RC channel directory does not exist: {channel_dir}")

    releases = sorted(
        (path for path in channel_dir.iterdir() if path.is_dir()),
        key=lambda path: rc_version_key(path.name),
    )
    manifest_path = channel_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"RC manifest does not exist: {manifest_path}")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("channel") != "rc":
        raise RuntimeError("RC manifest does not identify the rc channel")
    manifest_version = manifest.get("version")
    if not isinstance(manifest_version, str):
        raise RuntimeError("RC manifest does not contain a version")

    retained = releases[-keep:]
    retained_versions = {path.name for path in retained}
    if manifest_version not in retained_versions:
        raise RuntimeError(
            f"RC manifest version {manifest_version} is not among the latest {keep} releases"
        )
    return releases[:-keep]


def prune_releases(
    channel_dir: pathlib.Path,
    keep: int,
    dry_run: bool = False,
) -> list[str]:
    releases = releases_to_prune(channel_dir, keep)
    for release in releases:
        action = "Would remove" if dry_run else "Removing"
        print(f"{action} {release.name}")
        if not dry_run:
            shutil.rmtree(release)
    return [release.name for release in releases]


def main() -> None:
    args = parse_args()
    prune_releases(
        args.artifacts_dir / "agent" / "rc",
        keep=args.keep,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
