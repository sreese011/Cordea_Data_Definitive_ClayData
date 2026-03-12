# DevicePilot

DevicePilot is an internal tool for automated QA on mobile applications (Android + iOS). It is currently under active development.

## Source project

- Local path: `C:\Dev\DevicePilot`

## What it provides

- Remote mobile device operations for testing
- AI-assisted workflows for app QA
- MCP launcher support for Cursor

## Key references

- Main readme: `C:\Dev\DevicePilot\README.md`
- MCP config: `C:\Dev\DevicePilot\.cursor\mcp.json`
- Launch script: `C:\Dev\DevicePilot\.tools\launch-devicepilot.ps1`

## Typical usage

1. Open `C:\Dev\DevicePilot` in Cursor.
2. Start the stack with the launcher script:
   - `.\.tools\launch-devicepilot.ps1`
3. Use project docs for environment/device prerequisites.

## When to use DevicePilot

- Regression testing of mobile flows
- Repro and verification for app defects
- Automated smoke checks for Android/iOS app behavior

## Notes

- Keep implementation/status notes in the DevicePilot repo itself.
- This file is onboarding guidance, not the source of truth for code behavior.
