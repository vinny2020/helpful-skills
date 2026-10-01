# Xcode Device Hub skill

A reusable agent skill for the Xcode 26-to-27 simulator transition. It teaches an agent to probe the installed layout before diagnosing anything, to tell sandbox failures from broken installations, and to check an app's UI through simctl + XCTest when desktop automation can't attach — or when the check needs taps and typing, which simctl can't send.

Verified on Xcode 27.0 (27A266a) on two Macs, with iPhone 18 Pro and iPhone 18 Pro Max simulators on iOS 27.0. Version-specific claims and the older-runtime forum report are qualified in [the evidence notes](references/sources-and-scope.md).

## Install

Keep `SKILL.md`, `references/`, and `scripts/` together. `agents/openai.yaml` is optional metadata for Codex.

| Agent | Where to put this folder | How to use it |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/xcode-device-hub/` (all projects) or `.claude/skills/xcode-device-hub/` (one project) | Picked up automatically in new sessions; or ask for it by name. |
| Codex | `~/.codex/skills/xcode-device-hub/` or your configured skills directory | `Use $xcode-device-hub to check my app in Xcode 27.` |
| Any other agent | Anywhere it can read files | Point it at `SKILL.md`, e.g. "Follow xcode-device-hub/SKILL.md to check my app on the simulator." |

The skill doesn't depend on a particular agent or desktop automation tool, and it grants no permissions: the agent's own tooling and authorization rules still apply.

## Diagnose without changing anything

```sh
python3 scripts/diagnose.py            # full report (JSON)
python3 scripts/diagnose.py --redact   # masks simulator UDIDs and your home path, for sharing
python3 scripts/diagnose.py --no-simctl
```

It needs only Python 3 and Apple's command-line tools; no pip packages. It runs three read-only commands (`xcode-select -p`, `xcodebuild -version`, `xcrun simctl list --json`) and reads app bundles' `Info.plist` files. It doesn't boot, erase, or install anything, change `xcode-select`, write files, use the network, or call sudo. Running `simctl` can start Apple's background simulator service, which is normal.

If the agent's sandbox blocks CoreSimulator, use that environment's approved host-access mechanism; the script doesn't bypass permissions.

## Contents

- [SKILL.md](SKILL.md): discovery, failure classification, runtime choice, what each tool can do, reaching the screen safely, what makes a UI check real, cleanup.
- [The XCTest route](references/xctest-fallback.md): temporary UI tests in an existing target or a disposable project, exporting evidence, traps that pass silently, an optional interactive controller.
- [Sources and scope](references/sources-and-scope.md): what was observed on which installation, and the Apple forum report.
- [Diagnostic script](scripts/diagnose.py).

This package contains no credentials, private screenshots, or machine-specific identifiers.
