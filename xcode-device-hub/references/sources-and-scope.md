# Sources and scope

## Locally verified on 2026-09-30

The originating session used Xcode **27.0, build 27A266a**, and an **iPhone 18 Pro Max simulator running iOS 27.0**.

- `Contents/Developer/Applications/Simulator.app` was absent.
- `Contents/Applications/DeviceHub.app` existed. Its declared launcher was `DevicesTrampoline`; the main `DeviceHub` executable was also present.
- Xcode's Open Developer Tool menu listed Device Hub.
- Sandboxed `open` returned `kLSNoExecutableErr` despite the executable being present. The same bundle launch succeeded with approved host access.
- Sandboxed `simctl list` reported invalid CoreSimulator connections and denied log access. The same read-only command succeeded with approved host access.
- Desktop automation could not attach to Device Hub even though the user could click the simulated device. This was not evidence that the simulator was frozen.
- `xcrun simctl` could boot the device, install and launch a simulator app, and capture its screen.
- A temporary XCTest UI target could activate the app, inspect its accessibility tree, and perform coordinate taps, double taps, and label-based taps.
- A development client missing a native module was handled for the scoped check by using a compatible clean source snapshot. That result was kept distinct from testing a newer release binary.

## A second installation, 2026-09-30

A separate Mac on the same Xcode 27.0 build (27A266a) confirmed the layout: `Simulator.app` absent, `DeviceHub.app` present with `DevicesTrampoline` as its launcher, installed runtimes iOS 26.4, 26.5 and 27.0, and host-level `simctl list` working. A different agent used the existing-UI-test-target route on an iPhone 18 Pro running iOS 27.0: a temporary test file, the project's own launch-argument fixture (no sign-in), per-keystroke typing, and attachments exported with `xcresulttool`. It found a real problem unit tests had missed — an inline picker revealed while the software keyboard was still up appeared behind the keyboard.

These are observations from two installations, not a promise about every Xcode 27 build or automation connector. Probe the active installation and retain uncertainty when evidence differs.

## Apple Developer Forums

[iOS 17 simulator is unresponsive in Device Hub](https://developer.apple.com/forums/thread/844792)

The thread was read from a user-provided PDF saved on 2026-09-30 after online fetching failed. It reports unresponsive screen/home input for iOS 17 simulators in Xcode 27 beta, RC, and final releases. A participant cites release-note issue **181945323**, describing affected runtimes as earlier than iOS 18.0, tvOS 18.0, watchOS 11.0, and visionOS 2.0.

Another participant reports using the standalone Simulator app from a pre-27 Xcode, with the older simulator started from that app rather than Device Hub.

This is a community report, including a participant's attribution to release notes. It is not an independently verified Apple support guarantee. Recheck the thread and release notes for the installed patch version when this older-runtime issue matters. The original PDF is not redistributed with this skill.

## Local command references

Use installed help for version-specific behavior:

```sh
xcrun simctl help
xcrun simctl help io
xcrun simctl help install
xcrun simctl help get_app_container
xcodebuild -help
```

The skill discovers tool paths rather than requiring a hard-coded `/Applications/Xcode.app` installation.
