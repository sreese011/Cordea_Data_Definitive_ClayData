# CursorSetup

Company starter kit for onboarding a new developer workstation and standardizing Cursor behavior across projects.

## What this repository contains

- `cursor/project-baseline/`: project-level Cursor files to copy into every new repo (`.cursor/*` and `AGENTS.md`)
- `cursor/user/`: user-level Cursor desktop settings (`settings.json`, `keybindings.json`, optional snippets)
- `installers/`: installer source list (SharePoint links + official vendor links)
- `onboarding/new-pc/`: end-to-end setup checklist for a fresh Windows machine
- `tools/devicepilot/`: internal tool onboarding and usage guidance
- `linear/`: when and how to use Linear for planning and delivery

## Recommended usage

1. Clone this repo to the new machine.
2. Follow `onboarding/new-pc/NEW_PC_SETUP_CHECKLIST.md`.
3. Apply `cursor/user/*` into the Cursor user profile.
4. Copy `cursor/project-baseline/.cursor` and `cursor/project-baseline/AGENTS.md` into each new project repository.

## Notes

- Keep this repo updated as processes evolve.
- Do not store secrets, PATs, or credentials in this repository.
