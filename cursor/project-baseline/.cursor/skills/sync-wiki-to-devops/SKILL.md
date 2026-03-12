---
version: "1.0.0"
last_modified: "2026-02-21"
name: sync-wiki-to-devops
description: Sync local WIKI and optionally docs/knowledge to Azure DevOps Wiki. Use when the user says "sync wiki", "publish wiki", "push wiki to DevOps", or after updating docs/knowledge or WIKI. PAT is read from .env.
---

# Sync Wiki to Azure DevOps

## When to use

- User says "sync wiki", "publish wiki", "push wiki to DevOps", or "upload wiki".
- After creating or updating files in `docs/knowledge/` or `WIKI/` so the DevOps wiki stays in sync.

## Steps

1. From the **repo root** (e.g. `C:\dev\Cordea`), run:
   ```powershell
   .\"Azure Setup\Publish-WikiToDevOps.ps1"
   ```
   To include knowledge base pages:
   ```powershell
   .\"Azure Setup\Publish-WikiToDevOps.ps1" -IncludeKnowledge
   ```
2. The script reads PAT from `.env`; do not ask the user for a PAT.
3. Report success or any errors (e.g. which page was created/updated or failed).

## Notes

- If the user only updated `WIKI/`, the first command is enough. If they also updated `docs/knowledge/`, use `-IncludeKnowledge`.
