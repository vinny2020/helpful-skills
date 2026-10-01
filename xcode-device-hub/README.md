# Xcode Device Hub skill

A reusable agent skill for the Xcode 26-to-27 simulator transition. Discover Device Hub, distinguish sandbox failures from installation failures, and complete requested app checks when desktop automation cannot attach.

The workflow was exercised on Xcode 27.0 (27A266a) with an iPhone 18 Pro Max simulator running iOS 27.0. Version-specific claims and the older-runtime forum workaround are qualified in [the evidence notes](references/sources-and-scope.md).

## Install

This directory is a self-contained skill and can be the root of a GitHub repository. Keep `SKILL.md`, `agents/`, `references/`, and `scripts/` together.

For Codex, copy or clone this directory to `~/.codex/skills/xcode-device-hub`, or your configured skills directory. In a new session, invoke:

```text
Use $xcode-device-hub to run my iOS acceptance check in Xcode 27.
```

Other agents can read `SKILL.md` directly, subject to their own tooling and authorization rules. The skill does not require a particular desktop automation provider.

## Diagnose without changing the selected Xcode

```sh
python3 scripts/diagnose.py
```

Python 3 and Apple's installed command-line tools suffice; no pip packages are required. The script does not explicitly boot devices, install apps, erase data, or change system configuration. Normal tool invocation may start Apple's background services.

If the agent sandbox blocks CoreSimulator, use that environment's approved host-access mechanism. The script does not bypass permissions or invoke sudo. Review generated diagnostics before publishing local paths and device identifiers.

XCTest fallback requires a compatible simulator app. XcodeGen is optional, used only by the disposable-project example.

## Contents

- [SKILL.md](SKILL.md): discovery, diagnosis, runtime selection, provenance, and acceptance.
- [XCTest fallback](references/xctest-fallback.md): temporary tests and the verified controller pattern.
- [Sources and scope](references/sources-and-scope.md): local observations and the Apple forum report.
- [Diagnostic script](scripts/diagnose.py): installation, runtime, and device inspection.

This package excludes credentials, the original forum PDF, private app screenshots, and machine-specific test identifiers. Publishing the repository is a separate user action.
