---
version: "1.0.0"
last_modified: "2026-02-21"
name: extract-knowledge-from-transcript
description: Extract structured knowledge from a chat transcript into docs/knowledge. Use when the user pastes a transcript and wants learnings captured, or before starting a new chat to archive the current conversation.
---

# Extract Knowledge from Transcript

## When to use

- User pastes a chat transcript and asks to extract learnings, document what we did, or add to the knowledge base.
- User wants to "archive this chat" or "extract learnings before starting a new chat".

## Steps

1. Read the transcript (or use the current conversation if the user says "extract from this chat").
2. Create or update a file in `docs/knowledge/` using the template in `docs/knowledge/README.md`:
   - **What we were doing** (goal of the session)
   - **What worked (and why)**
   - **What didn't work (and why)**
   - **Decisions and tradeoffs**
   - **Files / scripts touched**
3. Save as `docs/knowledge/YYYY-MM-DD_short-topic.md` (e.g. `docs/knowledge/2026-02-11_lead-quote-script.md`).
4. Run the wiki sync so DevOps wiki is updated:
   ```powershell
   .\"Azure Setup\Publish-WikiToDevOps.ps1" -IncludeKnowledge
   ```
5. Confirm to the user: note created, path, and that wiki was synced.

## Rules

- Keep the note under one page; use bullets.
- Cite specific file names and decisions. Do not make up content that wasn't in the transcript or conversation.
