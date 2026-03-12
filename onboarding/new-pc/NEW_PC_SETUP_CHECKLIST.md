# New PC Setup Checklist

Use this checklist to get a developer productive quickly with the company Cursor setup.

## 1) Base software install

Install the standard tools listed in `installers/INSTALLERS.md`:

- Git
- PowerShell 7
- Node.js LTS
- Python 3
- GitHub CLI (`gh`)
- Azure CLI
- Cursor desktop

## 2) Repo and folder setup

- Create `C:\Dev`
- Clone `CursorSetup` into `C:\Dev\CursorSetup`
- Clone or copy active project repositories into `C:\Dev\...`

## 3) Cursor user configuration

Copy these files from this repo to the local Cursor user profile:

- Source: `cursor/user/settings.json`
- Target: `%APPDATA%\Cursor\User\settings.json`
- Source: `cursor/user/keybindings.json`
- Target: `%APPDATA%\Cursor\User\keybindings.json`

If snippets are added later:

- Source: `cursor/user/snippets/*`
- Target: `%APPDATA%\Cursor\User\snippets\`

## 4) Project configuration

For each new project, copy:

- `cursor/project-baseline/.cursor/` -> `<project-root>\.cursor\`
- `cursor/project-baseline/AGENTS.md` -> `<project-root>\AGENTS.md`

Commit these files into that project's git repo.

## 5) Internal tools and workflows

- DevicePilot: see `tools/devicepilot/README.md`
- Linear usage: see `linear/README.md`

## 6) Verification

- Open Cursor in a project that has `.cursor/` and `AGENTS.md`.
- Confirm project agents/rules are visible.
- Confirm custom keybinding works (`Ctrl+I` toggles agent mode).
- Run one normal dev workflow command in a project terminal.
