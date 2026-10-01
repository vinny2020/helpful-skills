---
name: xcode-device-hub
description: Locate and operate iOS simulator workflows across Xcode 26 and 27, including Device Hub, a missing Simulator.app, sandbox-related CoreSimulator failures, and a simctl + XCTest route for checking an app's UI when desktop automation can't attach or simctl can't send taps. Use for simulator setup, troubleshooting, or checking that an app behaves as intended on a simulator; not for general iOS implementation work.
---

# Xcode Device Hub

Get the intended app running on the intended simulator and verify its visible behavior. Probe the installed layout before diagnosing missing software: a changed tool layout is the most common way an outdated assumption turns into a confident wrong diagnosis.

## Discover the actual installation

Run `python3 scripts/diagnose.py` from this skill's directory. It reads the selected/effective developer directory, Xcode version, frontend bundles, runtimes, and devices. It does not boot, erase, install, or change the selected Xcode. Add `--redact` before sharing its output.

Treat these as separate facts:

- Xcode version and build number.
- Effective developer directory, including a possible `DEVELOPER_DIR` override.
- Frontend application: Simulator or Device Hub.
- Simulated device model, runtime version, UDID, and boot state.
- Application binary and source revision actually under test.

A device model name does not identify its OS runtime. Check the runtime grouping in `xcrun simctl list devices available` or its JSON output.

Observed layouts, to probe rather than assume:

| Frontend | Path relative to the developer directory |
| --- | --- |
| Traditional Simulator | `Applications/Simulator.app` |
| Xcode 27 Device Hub | `../Applications/DeviceHub.app` |

On Xcode 27.0, Device Hub is also in **Xcode > Open Developer Tool > Device Hub**, and the traditional Simulator.app path is absent. A missing old path alone does not mean Xcode is broken.

Once the bundle is confirmed present:

```sh
xcode_dev_dir="${DEVELOPER_DIR:-$(xcode-select -p)}"
open "$xcode_dev_dir/../Applications/DeviceHub.app"
```

Do not change the global `xcode-select` just to launch a frontend; use a per-command `DEVELOPER_DIR` when another installed version is needed.

## Classify failures before changing anything

| Evidence | Next action |
| --- | --- |
| Old Simulator.app path is absent | Probe Device Hub and the Xcode menu. |
| `open` reports `kLSNoExecutableErr`, but the declared executable exists or the app is visibly running | Suspect the execution environment (sandbox). Retry the exact launch through your environment's approved host-access mechanism. Do not recommend reinstalling yet. |
| `simctl` reports invalid CoreSimulator connections plus `Operation not permitted` | Suspect sandbox access. Retry the read-only device listing with approved access before diagnosing the service. |
| Host-level `simctl list` works and the device boots | CoreSimulator is fine; focus on the remaining frontend or app problem. |
| Desktop automation times out while a person can click the device | An automation attachment problem, not a frozen simulator. |
| Simulator boots but the app is absent | Install a compatible simulator build or build one. Booting is not checking the app. |
| The app's native layer doesn't match its source (for example a development client missing a native module) | Rebuild the client from the source under test. A JavaScript/asset reload cannot add native code. |

One meaningful retry or frontend restart is enough; repeating an identical attempt is not progress. Then use a different supported route or report the specific blocker. Don't force-quit a frontend a person is using just because an automation tool can't attach.

## Choose a usable runtime

A September 2026 Apple Developer Forums thread reports that Xcode 27 Device Hub ignores keyboard/mouse input for simulators older than iOS 18 (and older tvOS, watchOS, and visionOS); a reply cites release-note issue `181945323`. See [sources and scope](references/sources-and-scope.md) before treating this as current behavior in a later build.

When the task doesn't need an older OS, use an installed recent runtime. When reproducing an older-OS issue *is* the task, a newer runtime doesn't satisfy it; the reported workaround is the standalone Simulator app from a pre-27 Xcode. Verify locally; never replace or uninstall Xcode on your own initiative.

## Know what each tool can do

| Need | simctl | XCTest UI test | Desktop automation |
| --- | --- | --- | --- |
| Boot, install, launch, terminate | yes | launches its own target, or activates an installed app | via the frontend |
| Screenshot, video | yes (`simctl io`) | yes (attachments) | yes |
| Tap, type, swipe | **no** | yes | yes, when it can attach |
| Read the accessibility tree / assert on UI state | no | yes | partially |

So a check that needs input — typing into a field, tapping a button — needs XCTest when desktop automation can't attach. See [the XCTest route](references/xctest-fallback.md).

## Prepare the correct app

1. Read the repository's instructions, branch, commit, uncommitted changes, and existing worktrees. Test the intended change, not whatever checkout happens to be current. Use an isolated worktree or snapshot when needed, and preserve existing edits.
2. Pick the simulator by UDID and use that UDID in every mutating command. `booted` can hit the wrong device when several are running; don't shut down or reuse a simulator someone else booted.
3. Reuse a built `.app` only when it matches the source under test and was built for the simulator. A device or TestFlight binary is not a simulator binary.
4. If a dev server is involved (Metro, Vite, etc.), start it from the source under test with its existing configuration, without printing secrets. If you must test an older compatible snapshot instead, record that and never report it as a check of the newer build.

## Reach the screen under test safely

- Prefer the app's own test entry points — launch arguments, fixtures, preview or demo modes — over signing in. They are repeatable and touch no real data.
- Don't enter real credentials or one-time codes yourself. If a check genuinely needs a signed-in session, ask the person to sign in, then work read-only: open forms, type, cancel; don't save or publish.
- If the project has a UI test target, put a temporary test file there in a throwaway worktree and don't commit it. Otherwise use a disposable harness project (see the XCTest route).

## Verify interaction

Prefer a desktop control tool when it can attach. If it can't, and your environment's policy permits another method, use simctl for lifecycle and screenshots and XCTest for input and inspection. If that policy requires explicit authorization for alternative UI automation, get it once for the agreed scope. This skill grants no permissions.

What makes a UI check real:

- **Assert the resulting state, not the input.** "Tap delivered" or "test passed" isn't a result; the field's value, the visible sheet title, the switch's state are. A tap on a control's label can complete without changing the control — inspect it.
- **Type the way a person does.** Send text one character at a time when the code reacts to each keystroke; pasting a whole string can hide bugs in intermediate states.
- **Look for things covering the result.** The software keyboard, system alerts, permission prompts, and development-client banners can hide the very control you just revealed. If an element exists but isn't hittable, it's covered or off-screen — say which.
- **Check both directions.** Opening a sheet and closing it, entering a value and clearing it, invalid input and its recovery.
- **Keep evidence.** Screenshots or accessibility snapshots for each asserted state. Export XCTest attachments with `xcrun xcresulttool export attachments`.

## Finish with evidence and cleanup

Record the Xcode build, simulator model and runtime, source commit, app build, the transitions checked, and what remains unchecked (for example a physical device). Keep simulator evidence separate from physical-device evidence.

Restore settings you changed, shut down simulators you booted, remove temporary harness files and worktrees, and stop servers you started. Don't stop processes you didn't start.

Report the actual result. A simulator launching, a harness passing, or a different build working is not the same as the requested behavior being verified.
