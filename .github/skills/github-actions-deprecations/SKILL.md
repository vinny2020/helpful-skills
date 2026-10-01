# GitHub Actions deprecations

## When to use this skill

Use this skill when a workflow fails after a GitHub Actions platform change, especially around runner, action, or YAML deprecations.

## Recent breaking changes to watch for

- Older runner images or deprecated Node versions in actions can fail unexpectedly.
- Some workflow syntax or default behaviors change when GitHub updates its platform.
- Actions pinned to older versions may need refreshes to continue running reliably.
- Environment variables, permissions, and checkout behavior are common sources of CI regressions.

## What to check

1. Review the workflow file for deprecated actions or outdated runner versions.
2. Check the exact action `uses` references and whether a newer major version is required.
3. Verify permissions, shell behavior, and environment assumptions across jobs.
4. Run the workflow again in CI after each targeted migration change.

## Migration checklist

- Pin to supported action versions.
- Update image or runner configuration where necessary.
- Replace deprecated patterns with current equivalents.
- Validate the workflow after the smallest possible change set.

## Example validation workflow checks

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
```
