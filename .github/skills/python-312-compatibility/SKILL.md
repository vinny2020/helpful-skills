# Python 3.12 compatibility

## When to use this skill

Use this skill when upgrading a Python project to Python 3.12 or newer and encountering breaking changes in syntax, dependencies, or packaging.

## Recent breaking changes to watch for

- Some libraries that rely on old import semantics or deprecated behavior need explicit updates.
- Packaging metadata and dependency constraints may need refreshes for modern Python versions.
- Code paths using `distutils` or other removed APIs can fail under 3.12.
- CI and local shells may still be pointing at older Python interpreters.

## What to check

1. Confirm the target interpreter version in the project config and CI setup.
2. Review import paths and deprecated standard-library APIs.
3. Reinstall dependencies in a clean environment with the new Python version.
4. Run the project’s focused validation commands under Python 3.12 before broad rollout.

## Migration checklist

- Update Python version pinning and CI matrices.
- Remove or replace deprecated library behavior.
- Refresh dependency locks or constraints for the newer interpreter.
- Validate tests in a clean environment before merging.

## Example validation commands

```bash
python3 --version
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
python3 -m pytest
```
