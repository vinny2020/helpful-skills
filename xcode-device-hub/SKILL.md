---
name: xcode-device-hub
description: Locate and operate iOS simulator workflows across Xcode 26 and 27, including Device Hub, missing Simulator.app paths, sandbox-related CoreSimulator failures, and XCTest fallback when desktop automation cannot attach. Use for simulator setup, troubleshooting, or requested app acceptance checks; not for general iOS implementation work.
---

# Xcode Device Hub

Get the requested app running on the intended simulator and verify its visible behavior. Discover the installed layout before diagnosing missing software.

## Discover the actual installation

Run `python3 scripts/diagnose.py` from this skill's directory. It reads the selected/effective developer directory, Xcode version, frontend bundles, runtimes, and devices. It does not explicitly boot, erase, install, or change the selected Xcode.

Treat these as separate facts:

- Xcode version and build number.
- Effective developer directory, including a possible `DEVELOPER_DIR` override.
- Frontend application: Simulator or Device Hub.
- Simulated device model, runtime version, UUID, and boot state.
- Application binary and source revision actually under test.

An iPhone model name does not identify its iOS runtime. Check the runtime grouping in `xcrun simctl list devices available` or its JSON output.

Observed layouts, to probe rather than assume:

| Frontend | Path relative to the developer directory |
| --- | --- |
| Traditional Simulator | `Applications/Simulator.app` |
| Xcode 27 Device Hub | `../Applications/DeviceHub.app` |

On the verified Xcode 27.0 build, Device Hub was also available in **Xcode > Open Developer Tool > Device Hub**. The traditional Simulator.app path was absent. A missing old path alone does not establish a broken Xcode installation.

For the selected installation, once the bundle is confirmed present:

```sh
xcode_dev_dir="$(xcode-select -p)"
open "$xcode_dev_dir/../Applications/DeviceHub.app"
```

If `DEVELOPER_DIR` is set, use its resolved developer directory instead. Do not change global `xcode-select` merely to launch a frontend; prefer a per-command override when another installed version is needed.

## Classify failures before changing anything

| Evidence | Next action |
| --- | --- |
| Old Simulator.app path is absent | Probe Device Hub and the installed Xcode menu. |
| `open` reports `kLSNoExecutableErr`, but the declared executable exists or the app is visibly running | Check the execution environment. Retry the exact launch through the approved host-access mechanism. Do not recommend reinstalling yet. |
| `simctl` reports invalid CoreSimulator connections plus `Operation not permitted` | Suspect sandbox access. Retry the read-only device listing with approved access before diagnosing the service. |
| Host-level `simctl list` works and the device boots | CoreSimulator is available; focus on the remaining frontend or app problem. |
| Desktop automation times out while the user can click the device | Treat it as an automation attachment problem. Do not describe the simulator as frozen. |
| Simulator boots but the app is absent | Install a compatible simulator build or build one. Boot success is not app acceptance. |
| Expo reports a missing native module | Match the development client's native modules to the source. Metro reload cannot add native code. |

Do not use repeated identical retries as progress. After one meaningful retry or frontend restart, use a different supported route or report the specific blocker. Avoid force-quitting a frontend the user can interact with merely because an automation connector cannot attach.

## Choose a usable runtime

The linked September 2026 forum thread reports that Xcode 27 Device Hub rejects keyboard/mouse input for simulators earlier than iOS 18, plus older tvOS, watchOS, and visionOS versions. A reply attributes this to release-note issue `181945323`. See [sources and scope](references/sources-and-scope.md) before treating this as current behavior in a later build.

For testing that does not require an older OS, use an installed compatible recent runtime. If reproducing an iOS 17 issue is the task, changing to iOS 27 does not satisfy it. The forum's reported workaround is a pre-27 Xcode's standalone Simulator app, starting the older simulator from that frontend rather than Device Hub. Verify locally; do not automatically replace or uninstall Xcode.

## Prepare the correct app

1. Inspect repository instructions, branch, commit, dirty changes, and existing worktrees. Test the intended fix, not whichever checkout happens to be current.
2. Confirm the selected simulator UUID. Use it explicitly in mutating simctl commands; `booted` can address the wrong device when several are running.
3. Reuse a simulator-compatible `.app` only when its native modules match the requested source. A physical-device/TestFlight binary is not automatically a simulator binary.
4. For Expo, identify the dev-client version and source commit. Start Metro from that source with existing development configuration, without printing secret values. Check the actual app screen after launch.
5. If newer source requires a missing native module, build a matching client. An earlier compatible source snapshot is acceptable only when it answers the requested check; record the changed scope and never report it as verification of the newer release binary.

Use an isolated snapshot or worktree when needed. Preserve existing edits. Record dependency or Metro overrides used in the temporary environment.

## Verify interaction

Prefer the available desktop control tool when it can attach. If it cannot, and the active tool policy permits another method, use simctl for lifecycle/screenshots and XCTest for UI inspection/input. If that policy requires explicit authorization for alternative UI automation, obtain it once and retain it for the agreed scope. This skill does not grant broader permissions.

Read [the XCTest fallback](references/xctest-fallback.md) for that route.

For map acceptance:

- Zoom until the intended marker is visibly present. Record its identity and the resulting sheet title, not just a successful tap command.
- Check the layer's visible state. A switch-label tap may complete without changing the switch; inspect it before proceeding.
- Verify overlay data actually renders when checking hit precedence.
- Distinguish an empty-map tap from a real parcel selection. Unshaded land can still be selectable.
- Verify transitions out of the selected sheet as well as opening it.
- Establish outcomes with UI assertions, screenshots, or accessibility snapshots. A controller test exiting without errors proves only that the controller ran.

## Finish with evidence and cleanup

Record Xcode build, simulator model/runtime, source commit, app binary version, tested transitions, and any remaining release/device gap. Separate physical-device and simulator evidence.

Restore test settings that you changed and stop test-owned runners and development servers. Do not stop unrelated user processes. Honor requests to close mirroring or IDE applications. Public skill packages should contain no personal paths, credentials, app screenshots, or private project identifiers.

Report the actual acceptance result. Do not mark an issue complete solely because the simulator launched, the harness passed, or a different build behaved correctly.
