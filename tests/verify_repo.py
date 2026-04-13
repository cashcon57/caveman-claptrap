#!/usr/bin/env python3
"""Local verification runner for caveman install surfaces."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CheckFailure(RuntimeError):
    pass


def section(title: str) -> None:
    print(f"\n== {title} ==")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        args,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise CheckFailure(
            f"Command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def read_json(path: Path) -> object:
    return json.loads(path.read_text())


def verify_synced_files() -> None:
    section("Synced Files")
    skill_source = ROOT / "skills/caveman-claptrap/SKILL.md"
    rule_source = ROOT / "rules/caveman-claptrap-activate.md"

    skill_copies = [
        ROOT / "caveman-claptrap/SKILL.md",
        ROOT / "plugins/caveman-claptrap/skills/caveman-claptrap/SKILL.md",
        ROOT / ".cursor/skills/caveman-claptrap/SKILL.md",
        ROOT / ".windsurf/skills/caveman-claptrap/SKILL.md",
    ]
    for copy in skill_copies:
        ensure(copy.read_text() == skill_source.read_text(), f"Skill copy mismatch: {copy}")

    rule_copies = [
        ROOT / ".clinerules/caveman-claptrap.md",
        ROOT / ".github/copilot-instructions.md",
    ]
    for copy in rule_copies:
        ensure(copy.read_text() == rule_source.read_text(), f"Rule copy mismatch: {copy}")

    with zipfile.ZipFile(ROOT / "caveman-claptrap.skill") as archive:
        ensure("caveman-claptrap/SKILL.md" in archive.namelist(), "caveman-claptrap.skill missing caveman-claptrap/SKILL.md")
        ensure(
            archive.read("caveman-claptrap/SKILL.md").decode("utf-8") == skill_source.read_text(),
            "caveman-claptrap.skill payload mismatch",
        )

    print("Synced copies and caveman-claptrap.skill zip OK")


def verify_no_upstream_collision_paths() -> None:
    section("Collision Paths")

    old_paths = [
        ROOT / "caveman.skill",
        ROOT / "caveman",
        ROOT / "caveman-compress",
        ROOT / "compress",
        ROOT / "commands/caveman.toml",
        ROOT / "commands/caveman-commit.toml",
        ROOT / "commands/caveman-review.toml",
        ROOT / ".clinerules/caveman.md",
        ROOT / ".cursor/rules/caveman.mdc",
        ROOT / ".windsurf/rules/caveman.md",
        ROOT / ".cursor/skills/caveman",
        ROOT / ".windsurf/skills/caveman",
        ROOT / "plugins/caveman",
        ROOT / "hooks/caveman-config.js",
        ROOT / "hooks/caveman-activate.js",
        ROOT / "hooks/caveman-mode-tracker.js",
        ROOT / "hooks/caveman-statusline.sh",
        ROOT / "hooks/caveman-statusline.ps1",
        ROOT / "scripts/caveman-codex-activate.js",
    ]

    for path in old_paths:
        ensure(not path.exists(), f"Legacy collision-prone path still present: {path}")

    print("Legacy collision-prone paths removed")


def verify_manifests_and_syntax() -> None:
    section("Manifests And Syntax")

    manifest_paths = [
        ROOT / ".agents/plugins/marketplace.json",
        ROOT / ".claude-plugin/plugin.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / ".codex/hooks.json",
        ROOT / "gemini-extension.json",
        ROOT / "plugins/caveman-claptrap/hooks.json",
        ROOT / "plugins/caveman-claptrap/.codex-plugin/plugin.json",
    ]
    for path in manifest_paths:
        read_json(path)

    run(["node", "--check", "hooks/caveman-claptrap-config.js"])
    run(["node", "--check", "hooks/caveman-claptrap-activate.js"])
    run(["node", "--check", "hooks/caveman-claptrap-mode-tracker.js"])
    run(["node", "--check", "scripts/caveman-claptrap-codex-activate.js"])
    run(["bash", "-n", "hooks/install.sh"])
    run(["bash", "-n", "hooks/uninstall.sh"])
    run(["bash", "-n", "hooks/caveman-claptrap-statusline.sh"])

    # Ensure install/uninstall scripts include caveman-claptrap-config.js
    install_sh = (ROOT / "hooks/install.sh").read_text()
    uninstall_sh = (ROOT / "hooks/uninstall.sh").read_text()
    ensure("caveman-claptrap-config.js" in install_sh, "install.sh missing caveman-claptrap-config.js")
    ensure("caveman-claptrap-config.js" in uninstall_sh, "uninstall.sh missing caveman-claptrap-config.js")

    print("JSON manifests and JS/bash syntax OK")


def verify_codex_activation_assets() -> None:
    section("Codex Activation Assets")

    source_hooks = read_json(ROOT / ".codex/hooks.json")
    plugin_hooks = read_json(ROOT / "plugins/caveman-claptrap/hooks.json")
    ensure(source_hooks == plugin_hooks, "Codex hooks mismatch between repo and plugin package")

    expected_command = "node ./scripts/caveman-claptrap-codex-activate.js"
    for path, manifest in [
        (ROOT / ".codex/hooks.json", source_hooks),
        (ROOT / "plugins/caveman-claptrap/hooks.json", plugin_hooks),
    ]:
        session_start = manifest.get("hooks", {}).get("SessionStart")
        ensure(isinstance(session_start, list) and session_start, f"{path} missing SessionStart hook")
        ensure(session_start[0]["type"] == "command", f"{path} SessionStart hook should be command")
        ensure(session_start[0]["command"] == expected_command, f"{path} SessionStart command mismatch")

    source_script = ROOT / "scripts/caveman-claptrap-codex-activate.js"
    plugin_script = ROOT / "plugins/caveman-claptrap/scripts/caveman-claptrap-codex-activate.js"
    ensure(plugin_script.exists(), "packaged Codex plugin missing activation script")
    ensure(
        source_script.read_text() == plugin_script.read_text(),
        "Codex activation script mismatch between repo and plugin package",
    )

    run(["node", "--check", "plugins/caveman-claptrap/scripts/caveman-claptrap-codex-activate.js"])
    source_output = run(["node", "scripts/caveman-claptrap-codex-activate.js"]).stdout
    plugin_output = run(["node", "plugins/caveman-claptrap/scripts/caveman-claptrap-codex-activate.js"]).stdout
    ensure(source_output == plugin_output, "Codex activation output mismatch")
    for marker in ("Claptrap", "stop claptrap", "wenyan-ultra"):
        ensure(marker in source_output, f"Codex activation missing marker: {marker}")

    print("Codex activation assets OK")


def verify_powershell_static() -> None:
    section("PowerShell Static Checks")
    install_text = (ROOT / "hooks/install.ps1").read_text()
    uninstall_text = (ROOT / "hooks/uninstall.ps1").read_text()
    statusline_text = (ROOT / "hooks/caveman-claptrap-statusline.ps1").read_text()

    ensure("caveman-claptrap-config.js" in install_text, "install.ps1 missing caveman-claptrap-config.js")
    ensure("caveman-claptrap-config.js" in uninstall_text, "uninstall.ps1 missing caveman-claptrap-config.js")
    ensure("caveman-claptrap-statusline.ps1" in install_text, "install.ps1 missing statusline.ps1")
    ensure("caveman-claptrap-statusline.ps1" in uninstall_text, "uninstall.ps1 missing statusline.ps1")
    ensure("-AsHashtable" not in install_text, "install.ps1 should stay compatible with Windows PowerShell 5.1")
    ensure(
        "powershell -ExecutionPolicy Bypass -File" in install_text,
        "install.ps1 missing PowerShell statusline command",
    )
    ensure("[CLAPTRAP" in statusline_text, "caveman-claptrap-statusline.ps1 missing badge output")

    print("Windows install path statically wired")


def load_compress_modules():
    sys.path.insert(0, str(ROOT / "caveman-claptrap-compress"))
    import scripts.benchmark  # noqa: F401
    import scripts.cli as cli
    import scripts.compress  # noqa: F401
    import scripts.detect as detect
    import scripts.validate as validate

    return cli, detect, validate


def verify_compress_fixtures() -> None:
    section("Compress Fixtures")
    _, detect, validate = load_compress_modules()

    fixtures = sorted((ROOT / "tests/caveman-compress").glob("*.original.md"))
    ensure(fixtures, "No caveman-compress fixtures found")

    for original in fixtures:
        compressed = original.with_name(original.name.replace(".original.md", ".md"))
        ensure(compressed.exists(), f"Missing compressed fixture for {original.name}")
        result = validate.validate(original, compressed)
        ensure(result.is_valid, f"Fixture validation failed for {compressed.name}: {result.errors}")
        ensure(detect.should_compress(compressed), f"Fixture should be compressible: {compressed.name}")

    print(f"Validated {len(fixtures)} caveman-compress fixture pairs")


def verify_compress_cli() -> None:
    section("Compress CLI")

    skip_result = run(
        ["python3", "-m", "scripts", "../hooks/install.sh"],
        cwd=ROOT / "caveman-claptrap-compress",
        check=False,
    )
    ensure(skip_result.returncode == 0, "compress CLI skip path should exit 0")
    ensure("Detected: code" in skip_result.stdout, "compress CLI skip path missing detection output")
    ensure(
        "Skipping: file is not natural language" in skip_result.stdout,
        "compress CLI skip path missing skip output",
    )

    missing_result = run(
        ["python3", "-m", "scripts", "../does-not-exist.md"],
        cwd=ROOT / "caveman-claptrap-compress",
        check=False,
    )
    ensure(missing_result.returncode == 1, "compress CLI missing-file path should exit 1")
    ensure("File not found" in missing_result.stdout, "compress CLI missing-file output mismatch")

    print("Compress CLI skip/error paths OK")


def verify_hook_install_flow() -> None:
    section("Claude Hook Flow")

    ensure(shutil.which("node") is not None, "node is required for hook verification")
    ensure(shutil.which("bash") is not None, "bash is required for hook verification")

    with tempfile.TemporaryDirectory(prefix="caveman-verify-") as temp_root:
        temp_root_path = Path(temp_root)
        home = temp_root_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)

        existing_settings = {
            "statusLine": {"type": "command", "command": "bash /tmp/existing-statusline.sh"},
            "hooks": {"Notification": [{"hooks": [{"type": "command", "command": "echo keep-me"}]}]},
        }
        (claude_dir / "settings.json").write_text(json.dumps(existing_settings, indent=2) + "\n")

        run(["bash", "hooks/install.sh"], env={"HOME": str(home)})

        settings = read_json(claude_dir / "settings.json")
        hooks = settings["hooks"]
        ensure(settings["statusLine"]["command"] == "bash /tmp/existing-statusline.sh", "install.sh clobbered existing statusLine")
        ensure("SessionStart" in hooks, "SessionStart hook missing after install")
        ensure("UserPromptSubmit" in hooks, "UserPromptSubmit hook missing after install")

        activate = run(
            ["node", "hooks/caveman-claptrap-activate.js"],
            env={"HOME": str(home)},
        )
        ensure("CLAPTRAP MODE ACTIVE" in activate.stdout, "activation output missing Claptrap banner")
        ensure("stop claptrap" in activate.stdout, "activation output missing claptrap deactivation")
        ensure("wenyan-ultra" in activate.stdout, "activation output missing wenyan support")
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "activation should stay quiet when custom statusline exists")
        ensure((claude_dir / ".caveman-claptrap-active").read_text() == "full", "activation flag should default to full")

        # Test configurable default mode via CLAPTRAP_DEFAULT_MODE env var
        activate_custom = run(
            ["node", "hooks/caveman-claptrap-activate.js"],
            env={"HOME": str(home), "CLAPTRAP_DEFAULT_MODE": "ultra"},
        )
        ensure("CLAPTRAP MODE ACTIVE" in activate_custom.stdout, "activation with custom default missing banner")
        ensure((claude_dir / ".caveman-claptrap-active").read_text() == "ultra", "CLAPTRAP_DEFAULT_MODE=ultra should set flag to ultra")
        # Test "off" mode — activation skipped, flag removed
        activate_off = run(
            ["node", "hooks/caveman-claptrap-activate.js"],
            env={"HOME": str(home), "CLAPTRAP_DEFAULT_MODE": "off"},
        )
        ensure("CLAPTRAP MODE ACTIVE." not in activate_off.stdout, "off mode should not emit Claptrap banner")
        ensure(not (claude_dir / ".caveman-claptrap-active").exists(), "off mode should remove flag file")

        # Test mode tracker with /claptrap when default is off — should NOT write flag
        subprocess.run(
            ["node", "hooks/caveman-claptrap-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "CLAPTRAP_DEFAULT_MODE": "off"},
            text=True,
            input='{"prompt":"/claptrap"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".caveman-claptrap-active").exists(), "/claptrap with off default should not write flag")

        # Reset back to full for subsequent tests
        (claude_dir / ".caveman-claptrap-active").write_text("full")

        run(
            ["node", "hooks/caveman-claptrap-mode-tracker.js"],
            env={"HOME": str(home)},
            check=True,
        )

        ultra_prompt = subprocess.run(
            ["node", "hooks/caveman-claptrap-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/claptrap ultra"}',
            capture_output=True,
            check=True,
        )
        ensure(ultra_prompt.stdout == "", "mode tracker should stay silent")
        ensure((claude_dir / ".caveman-claptrap-active").read_text() == "ultra", "mode tracker did not record ultra")

        legacy_prompt = subprocess.run(
            ["node", "hooks/caveman-claptrap-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/caveman wenyan"}',
            capture_output=True,
            check=True,
        )
        ensure(legacy_prompt.stdout == "", "legacy caveman alias should stay silent")
        ensure((claude_dir / ".caveman-claptrap-active").read_text() == "wenyan", "legacy caveman alias should still work")

        subprocess.run(
            ["node", "hooks/caveman-claptrap-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"normal mode"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".caveman-claptrap-active").exists(), "normal mode should remove flag file")

        (claude_dir / ".caveman-claptrap-active").write_text("wenyan-ultra")
        statusline = run(
            ["bash", "hooks/caveman-claptrap-statusline.sh"],
            env={"HOME": str(home)},
        )
        ensure("[CLAPTRAP:WENYAN-ULTRA]" in statusline.stdout, "statusline badge output mismatch")

        reinstall = run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        ensure("Nothing to do" in reinstall.stdout, "install.sh should be idempotent")

        run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        settings_after = read_json(claude_dir / "settings.json")
        ensure(settings_after == existing_settings, "uninstall.sh did not restore non-Claptrap settings")
        ensure(not (claude_dir / ".caveman-claptrap-active").exists(), "uninstall.sh should remove flag file")

    with tempfile.TemporaryDirectory(prefix="caveman-verify-fresh-") as temp_root:
        home = Path(temp_root) / "home"
        run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        claude_dir = home / ".claude"
        settings = read_json(claude_dir / "settings.json")
        ensure("statusLine" in settings, "fresh install should configure statusline")
        activate = run(["node", "hooks/caveman-claptrap-activate.js"], env={"HOME": str(home)})
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "fresh install should not nudge for statusline")
        run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        ensure(read_json(claude_dir / "settings.json") == {}, "fresh uninstall should leave empty settings")

    print("Claude hook install/uninstall flow OK")


def main() -> int:
    checks = [
        verify_synced_files,
        verify_no_upstream_collision_paths,
        verify_manifests_and_syntax,
        verify_codex_activation_assets,
        verify_powershell_static,
        verify_compress_fixtures,
        verify_compress_cli,
        verify_hook_install_flow,
    ]

    try:
        for check in checks:
            check()
    except CheckFailure as exc:
        print(f"\nFAIL: {exc}", file=sys.stderr)
        return 1

    print("\nAll local verification checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
