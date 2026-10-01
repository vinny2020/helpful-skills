# The XCTest route: input and inspection without desktop automation

`simctl` can boot, install, launch, and screenshot, but it cannot tap or type. When a check needs input and no desktop automation tool can attach, drive the app from an XCTest UI test. Use this route only when the simulator and app are available and your environment's rules permit it.

Keep every harness file temporary: in a throwaway worktree or a disposable project, never committed to the product.

## 1. Prepare the device and app

Take the simulator UDID and runtime from the diagnostic report.

```sh
xcrun simctl list devices available
xcrun simctl boot "$SIMULATOR_UDID"            # skip if already booted
xcrun simctl get_app_container "$SIMULATOR_UDID" "$APP_BUNDLE_ID" app
xcrun simctl install "$SIMULATOR_UDID" "$SIMULATOR_APP_PATH"   # only if absent
xcrun simctl launch "$SIMULATOR_UDID" "$APP_BUNDLE_ID"
xcrun simctl io "$SIMULATOR_UDID" screenshot "$EVIDENCE_DIR/before.png"
```

These variables are task inputs, not defaults to guess. If commands fail with access errors, resolve the execution context before touching system services.

## 2. Choose where the test lives

**Preferred: the project's existing UI test target.** Add one temporary test file in a throwaway worktree. You get the project's build settings and, often, its test entry points (launch arguments, fixtures, preview modes) that reach a screen without signing in. `xcodebuild test -only-testing:<Target>/<Class>` runs just that file.

**Otherwise: a disposable harness project** that activates the already-installed app by bundle identifier. With XcodeGen:

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

Without XcodeGen, create the equivalent UI-testing bundle in Xcode. Set the deployment target no higher than the chosen runtime, and don't add a product dependency just for the harness.

## 3. Write a test that asserts outcomes

```swift
import XCTest

final class AcceptanceTests: XCTestCase {
    private func evidence(_ name: String) {
        let shot = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        shot.name = name
        shot.lifetime = .keepAlways
        add(shot)
    }

    func testRequestedInteraction() throws {
        // Existing target: XCUIApplication() with the project's test launch arguments.
        // Disposable harness: XCUIApplication(bundleIdentifier: "YOUR_APP_BUNDLE_ID"), then .activate().
        let app = XCUIApplication()
        app.launchArguments = ["-YourFixtureArgument"]
        app.launch()
        print(app.debugDescription)          // find real labels before asserting on them

        let field = app.textFields["Observed label"]
        XCTAssertTrue(field.waitForExistence(timeout: 10))
        field.tap()
        for ch in "03/18/1931" { field.typeText(String(ch)) }   // one keystroke at a time
        XCTAssertEqual(field.value as? String, "03/18/1931")
        evidence("after-typing")
    }
}
```

This is a scaffold. Replace the labels and assertions with the ones the task needs, found in `app.debugDescription` rather than guessed.

Run it, with a fresh result bundle each time and verbose output sent to a log:

```sh
xcodebuild test \
  -project "$PROJECT" -scheme "$SCHEME" \
  -destination "platform=iOS Simulator,id=$SIMULATOR_UDID" \
  -only-testing:"$UI_TEST_TARGET/$TEST_CLASS" \
  -parallel-testing-enabled NO \
  -resultBundlePath "$EVIDENCE_DIR/results.xcresult" > "$EVIDENCE_DIR/test.log" 2>&1
xcrun xcresulttool export attachments \
  --path "$EVIDENCE_DIR/results.xcresult" --output-path "$EVIDENCE_DIR/attachments"
```

`manifest.json` in the export maps each attachment's name to its exported file. Look at the screenshots: a passing test can still hide a problem the assertions didn't cover.

## Traps that pass silently

- **Below the fold.** An element can exist without being hittable; `tap()` on it does nothing and raises no error. Scroll until `isHittable` before tapping.
- **Label vs control.** A form row's frame can span the whole row, so `tap()` lands on the label and a switch doesn't flip. Tap the control's coordinate and assert its new value.
- **Covered by the keyboard or an alert.** After revealing something (a picker, a sheet), check it's hittable. If not, find what covers it — often the software keyboard is still up. Report it: a person would hit it too.
- **Clearing a field.** Put the cursor at the end (for right-aligned text, tap near the right edge), then send `XCUIKeyboardKey.delete` once per character.
- **Bulk vs per-keystroke input.** Code that reacts to each keystroke can behave differently when the whole string arrives at once; type one character at a time.

## Optional: an interactive controller

When the screen is unfamiliar and rebuilding for every tap is slow, a short-lived test can act as a controller:

1. Activate the app; write `app.debugDescription` and a screenshot into the runner's Documents directory, and print that path.
2. For a bounded session (say 15 minutes), poll a small `command.json` there. Accept only a fixed whitelist (inspect, tap, double tap, drag, label tap, finish). Never accept arbitrary code or open a network listener.
3. Give each command a unique ID, execute it once, refresh the tree and screenshot, then atomically write a matching completion ID. Acknowledge `finish` before returning.
4. The host writes commands atomically and waits for the matching ID with a finite timeout. A timeout is not success; read the runner log before retrying.
5. Decide each next step from the new screenshot and tree. Keep acceptance assertions separate from the controller's own pass/fail.

Useful primitives:

```swift
let point = app.coordinate(withNormalizedOffset: CGVector(dx: x, dy: y))   // 0...1, relative to the app frame
point.tap()
point.doubleTap()
point.press(forDuration: 0.1, thenDragTo: endPoint)
app.descendants(matching: .any)
    .matching(NSPredicate(format: "label == %@", observedLabel))
    .firstMatch.tap()
```

Coordinates are relative to the app frame, not the Device Hub window. Re-derive them from the latest screenshot after any layout change, scroll, or rotation.

## Cleanup

End any controller and confirm the runner exited. Shut down simulators you booted, remove harness files and worktrees, stop servers you started, and restore changed settings. Keep the screenshots, source commit, build and runtime identity, and the assertions you actually made.
