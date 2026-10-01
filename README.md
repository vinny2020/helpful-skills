# helpful-skills

A collection of AI skills focused on recent breaking changes across common developer toolchains and platforms.

This repository is intentionally small and practical: each skill documents the migration surface, the most common failure modes, and the checks to run after updating code or CI.

## Included skills

- Node.js 20 and modern runtime compatibility
- GitHub Actions deprecations and runner changes
- Python 3.12+ compatibility updates

## Structure

The skill collection lives under `.github/skills/` and follows a simple pattern:

- `.github/skills/<skill-name>/SKILL.md`

Each skill file is written to be used by an AI coding assistant or developer during a migration or upgrade effort.
