# XCTest fallback when desktop attachment fails

Use this after the intended simulator and app are available, and alternative UI automation is authorized under the active environment's rules. Keep the harness in a temporary directory; it should not alter the product's source or tests.

## Device and app preparation

Get the simulator UUID and runtime from the diagnostic report. Check state before booting:

```sh
xcrun simctl list devices available
xcrun simctl boot "$SIMULATOR_UDID"
xcrun simctl get_app_container "$SIMULATOR_UDID" "$APP_BUNDLE_ID" app
# If absent, use a known simulator-compatible binary:
xcrun simctl install "$SIMULATOR_UDID" "$SIMULATOR_APP_PATH"
xcrun simctl launch "$SIMULATOR_UDID" "$APP_BUNDLE_ID"
xcrun simctl io "$SIMULATOR_UDID" screenshot "$EVIDENCE_DIR/before.png"
```

These variables are task inputs, not defaults to guess. A booted device needs no second boot. If commands fail with access errors, resolve the execution context before repairing system services.

## Disposable test target

If XcodeGen is available, this project shape was verified on Xcode 27.0. Otherwise use an authorized existing UI test target or create the equivalent Xcode project. Do not add a product dependency solely for this harness.

```yaml
name: SimulatorAcceptance
options:
  deploymentTarget:
    iOS: '18.0'
settings:
  base:
    CODE_SIGNING_ALLOWED: NO
    SWIFT_VERSION: '5.0'
targets:
  AcceptanceUITests:
    type: bundle.ui-testing
    platform: iOS
    sources: [Tests]
    settings:
      base:
        PRODUCT_BUNDLE_IDENTIFIER: dev.agent.AcceptanceUITests
        GENERATE_INFOPLIST_FILE: YES
schemes:
  SimulatorAcceptance:
    build:
      targets:
        AcceptanceUITests: [test]
    test:
      targets: [AcceptanceUITests]
```

Use a task-specific runner identifier if a similarly named harness is installed. Set the deployment target low enough for the chosen runtime.

An independent UI test can inspect an installed app without building it as a target dependency:

```swift
import XCTest

final class AcceptanceTests: XCTestCase {
    func testRequestedInteraction() throws {
        let app = XCUIApplication(bundleIdentifier: "YOUR_APP_BUNDLE_ID")
        app.activate()
        // Add the actual action and observable assertions for this task.
        // Use a label only after observing it in app.debugDescription.
        print(app.debugDescription)
        let evidence = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        evidence.name = "observed-app-state"
        evidence.lifetime = .keepAlways
        add(evidence)
    }
}
```

This snippet is a scaffold, not a passing acceptance test. Add meaningful assertions, such as the expected sheet title appearing and the previous sheet disappearing.

```sh
xcodegen generate --spec "$HARNESS_DIR/project.yml"
xcodebuild test \
  -project "$HARNESS_DIR/SimulatorAcceptance.xcodeproj" \
  -scheme SimulatorAcceptance \
  -destination "platform=iOS Simulator,id=$SIMULATOR_UDID" \
  -derivedDataPath "$HARNESS_DIR/build" \
  -parallel-testing-enabled NO \
  -resultBundlePath "$HARNESS_DIR/results.xcresult"
```

Use a new result bundle path for each run. Redirect verbose build output to a task-local log and inspect errors and the final result. Long commands should yield so progress can still be reported.

## Interactive controller pattern

For an unfamiliar map, a short-lived XCTest controller avoids rebuilding for every tap. The originating session verified this pattern:

1. Activate `XCUIApplication(bundleIdentifier:)` and write `app.debugDescription` and `XCUIScreen.main.screenshot().pngRepresentation` into the runner's Documents directory. Print that directory's path.
2. Poll a small `command.json` there for a bounded session, such as 15 minutes. Whitelist inspect, tap, double tap, drag, label tap, and finish. Do not accept arbitrary code or expose a remote listener.
3. Give each command a unique ID and execute it once. Refresh the tree and screenshot, then atomically write a matching completion ID. Acknowledge `finish` before returning.
4. The host writes commands atomically and waits for the matching ID with a finite timeout. A timeout is not success; inspect the runner log before retrying.
5. Inspect the new screenshot/tree before deciding the next action. Record acceptance assertions separately from the controller's own test status.

Useful XCTest primitives:

```swift
let point = app.coordinate(withNormalizedOffset: CGVector(dx: x, dy: y))
point.tap()
point.doubleTap()
point.press(forDuration: 0.1, thenDragTo: endPoint)
app.descendants(matching: .any)
    .matching(NSPredicate(format: "label == %@", observedLabel))
    .firstMatch.tap()
```

Normalized coordinates are relative to the app frame, not the desktop Device Hub window. Use the latest screenshot and confirm orientation/frame; do not reuse coordinates after a camera move or layout change. Validate coordinates are between 0 and 1 and prefer exact visible controls when practical.

In the verified run, a switch-label action completed without visibly changing the switch. A direct coordinate tap changed it. Inspect the resulting switch and rendered layer; successful input delivery alone does not prove a state transition.

Development-client prompts or system alerts may sit above the app. Handle the observed prompt before continuing. Do not label a hidden-map tap as a map test.

## Cleanup and evidence

End the controller, verify the runner exits, stop only the Metro/test processes started for the task, and restore changed preferences. Preserve screenshots, source commit, binary/runtime identity, and actual assertions. A development client serving a clean commit remains distinct from a release/TestFlight build.
