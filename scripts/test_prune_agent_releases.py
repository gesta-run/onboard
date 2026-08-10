import json
import pathlib
import tempfile
import unittest

from scripts.prune_agent_releases import prune_releases, rc_version_key


class PruneAgentReleasesTest(unittest.TestCase):
    def create_channel(
        self,
        root: pathlib.Path,
        versions: list[str],
        manifest_version: str,
    ) -> pathlib.Path:
        channel = root / "agent" / "rc"
        channel.mkdir(parents=True)
        for version in versions:
            (channel / version).mkdir()
        (channel / "manifest.json").write_text(
            json.dumps({"channel": "rc", "version": manifest_version})
        )
        return channel

    def test_rc_version_key_sorts_numbers_numerically(self) -> None:
        versions = ["0.0.1-rc9", "0.0.2-rc1", "0.0.1-rc10"]

        self.assertEqual(
            sorted(versions, key=rc_version_key),
            ["0.0.1-rc9", "0.0.1-rc10", "0.0.2-rc1"],
        )

    def test_prune_releases_keeps_latest_versions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            versions = [f"0.0.1-rc{number}" for number in range(1, 13)]
            channel = self.create_channel(root, versions, "0.0.1-rc12")

            removed = prune_releases(channel, keep=10)

            self.assertEqual(removed, ["0.0.1-rc1", "0.0.1-rc2"])
            self.assertEqual(
                {path.name for path in channel.iterdir() if path.is_dir()},
                set(versions[2:]),
            )

    def test_dry_run_does_not_remove_releases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            versions = [f"0.0.1-rc{number}" for number in range(1, 4)]
            channel = self.create_channel(root, versions, "0.0.1-rc3")

            removed = prune_releases(channel, keep=2, dry_run=True)

            self.assertEqual(removed, ["0.0.1-rc1"])
            self.assertTrue((channel / "0.0.1-rc1").is_dir())

    def test_prune_releases_rejects_manifest_outside_retention(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            versions = [f"0.0.1-rc{number}" for number in range(1, 4)]
            channel = self.create_channel(root, versions, "0.0.1-rc1")

            with self.assertRaisesRegex(RuntimeError, "not among the latest 2"):
                prune_releases(channel, keep=2)

            self.assertEqual(
                {path.name for path in channel.iterdir() if path.is_dir()},
                set(versions),
            )

    def test_prune_releases_rejects_unknown_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            channel = self.create_channel(root, ["0.0.1-rc1"], "0.0.1-rc1")
            (channel / "unexpected").mkdir()

            with self.assertRaisesRegex(ValueError, "invalid RC release directory"):
                prune_releases(channel, keep=1)


if __name__ == "__main__":
    unittest.main()
