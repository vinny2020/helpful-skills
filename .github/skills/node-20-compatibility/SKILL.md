# Node.js 20 compatibility

## When to use this skill

Use this skill when upgrading a project to Node.js 20 or newer, or when a runtime change causes failures in CI, local tooling, or production builds.

## Recent breaking changes to watch for

- `fs.rmdir` and recursive directory APIs were deprecated and may require explicit migration paths.
- Some packages assume older OpenSSL or older runtime behavior and fail under newer Node.js defaults.
- CI images and GitHub Actions runners may require updated tool versions or package manager flags.
- `npm` and `npx` behavior can differ in lockfile resolution, peer dependency warnings, and script execution.

## What to check

1. Confirm the runtime version in package manifests, CI configuration, and local dev docs.
2. Scan package scripts for assumptions about older Node.js semantics.
3. Update dependency ranges that pin old Node branches or unsupported engines.
4. Validate build, test, and lint steps on the target runtime before merging changes.

## Migration checklist

- Update the project engine requirement.
- Review deprecation warnings during install and test execution.
- Replace deprecated APIs where the project directly calls them.
- Re-run all validation commands in the same environment used by CI.

## Example validation commands

```bash
node --version
npm install
npm test
npm run build
```
