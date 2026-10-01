#!/usr/bin/env python3
"""Read Xcode/frontend/runtime metadata without changing simulator configuration."""

import argparse
import json
import os
from pathlib import Path
import plistlib
import subprocess


def run(argv, timeout):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return {"command": argv, "ok": result.returncode == 0,
                "exit_code": result.returncode, "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()[:6000]}
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"command": argv, "ok": False, "error": str(error)}


def frontend(path):
    result = {"bundle": str(path), "exists": path.is_dir()}
    if not result["exists"]:
        return result
    try:
        with (path / "Contents/Info.plist").open("rb") as stream:
            info = plistlib.load(stream)
        executable = info.get("CFBundleExecutable")
        result["bundle_id"] = info.get("CFBundleIdentifier")
        result["declared_executable"] = executable
        if executable:
            target = path / "Contents/MacOS" / executable
            result["executable_exists"] = target.is_file()
            result["executable_accessible"] = os.access(target, os.X_OK)
    except (OSError, ValueError, plistlib.InvalidFileException) as error:
        result["inspection_error"] = str(error)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-simctl", action="store_true", help="Only inspect Xcode and frontend bundles")
    parser.add_argument("--timeout", type=float, default=15, help="Per-command timeout in seconds (default: 15)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")

    selected = run(["xcode-select", "-p"], args.timeout)
    effective = os.environ.get("DEVELOPER_DIR") or selected.get("stdout")
    report = {
        "purpose": "Diagnosis only; not app acceptance or proof of frontend responsiveness",
        "selected_developer_directory": selected,
        "developer_dir_override": os.environ.get("DEVELOPER_DIR"),
        "xcode_version": run(["xcodebuild", "-version"], args.timeout),
    }
    if effective:
        developer = Path(effective).expanduser()
        if developer.suffix == ".app":
            developer = developer / "Contents/Developer"
        developer = developer.resolve()
        report["effective_developer_directory"] = str(developer)
        report["frontends"] = [
            frontend(developer / "Applications/Simulator.app"),
            frontend(developer.parent / "Applications/DeviceHub.app"),
            frontend(developer.parent / "Applications/Simulator.app"),
        ]

    if not args.no_simctl:
        simctl = run(["xcrun", "simctl", "list", "--json"], args.timeout)
        if simctl["ok"]:
            try:
                data = json.loads(simctl["stdout"])
                report["runtimes"] = [
                    {key: runtime.get(key) for key in ("identifier", "name", "version", "isAvailable", "availabilityError")}
                    for runtime in data.get("runtimes", [])
                ]
                report["devices_by_runtime"] = {
                    runtime: [
                        {key: device.get(key) for key in ("name", "udid", "state", "isAvailable", "deviceTypeIdentifier")}
                        for device in devices
                    ]
                    for runtime, devices in data.get("devices", {}).items()
                }
                del simctl["stdout"]
            except (TypeError, ValueError) as error:
                simctl["parse_error"] = str(error)
                simctl["stdout"] = simctl["stdout"][:6000]
        report["simctl"] = simctl

    report["interpretation"] = (
        "Check access context before diagnosing missing executables or broken services. "
        "Device model and OS runtime are separate. This report does not test input or the app."
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
