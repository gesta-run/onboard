import pathlib
import tempfile
import unittest

from scripts.prepare_agent_release import (
    platform_from_asset,
    rewrite_installers,
    update_channel_entrypoints,
    update_uninstall_entrypoints,
    write_checksums,
)


class PrepareAgentReleaseTest(unittest.TestCase):
    def test_platform_from_windows_asset(self) -> None:
        self.assertEqual(
            platform_from_asset("gesta-agent-windows-amd64.exe"),
            "windows/amd64",
        )

    def test_rewrite_installers_pins_release_url(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = pathlib.Path(temporary)
            (target / "install.sh").write_text(
                "install_base_url=${GESTA_AGENT_INSTALL_BASE_URL:-https://old.example}\n"
            )
            (target / "install-agent.ps1").write_text(
                '[string]$BaseUrl = "https://old.example"\n'
            )
            rewrite_installers(target, "rc", "0.0.1-rc81")
            expected = "https://artifacts.gesta.run/gesta/agent/rc/0.0.1-rc81"
            self.assertIn(expected, (target / "install.sh").read_text())
            self.assertIn(expected, (target / "install-agent.ps1").read_text())

    def test_update_channel_entrypoints_updates_both_platforms(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifacts = pathlib.Path(temporary)
            (artifacts / "install-agent.sh").write_text(
                "rc_version=0.0.1-rc80\nstable_version=0.1.0\n"
            )
            (artifacts / "install-agent.ps1").write_text(
                '$rcVersion = "0.0.1-rc80"\n$stableVersion = "0.1.0"\n'
            )

            update_channel_entrypoints(artifacts, "rc", "0.0.1-rc81")

            self.assertIn(
                "rc_version=0.0.1-rc81",
                (artifacts / "install-agent.sh").read_text(),
            )
            self.assertIn(
                '$rcVersion = "0.0.1-rc81"',
                (artifacts / "install-agent.ps1").read_text(),
            )

    def test_update_uninstall_entrypoints_copies_release_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = pathlib.Path(temporary)
            artifacts = root / "artifacts"
            release = root / "release"
            artifacts.mkdir()
            release.mkdir()
            (release / "uninstall.sh").write_text("#!/bin/sh\necho shell\n")
            (release / "uninstall-agent.ps1").write_text("Write-Host powershell\n")

            update_uninstall_entrypoints(artifacts, release)

            self.assertEqual(
                (artifacts / "uninstall-agent.sh").read_text(),
                "#!/bin/sh\necho shell\n",
            )
            self.assertEqual(
                (artifacts / "uninstall-agent.ps1").read_text(),
                "Write-Host powershell\n",
            )
            self.assertTrue((artifacts / "uninstall-agent.sh").stat().st_mode & 0o100)

    def test_write_checksums_includes_install_and_uninstall_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = pathlib.Path(temporary)
            (target / "bin").mkdir()
            for name in (
                "install.sh",
                "install-agent.ps1",
                "uninstall.sh",
                "uninstall-agent.ps1",
                "release.json",
            ):
                (target / name).write_text(name)

            checksums = write_checksums(target)

            self.assertEqual(
                set(checksums),
                {
                    "install.sh",
                    "install-agent.ps1",
                    "uninstall.sh",
                    "uninstall-agent.ps1",
                    "release.json",
                },
            )


if __name__ == "__main__":
    unittest.main()
