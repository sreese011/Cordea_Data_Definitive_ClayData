---
version: "1.0.0"
last_modified: "2026-02-21"
description: "Multi-agent setup guide with agent definitions, invocation methods, and worktree paths"
---

# Multi-agent setup (Cursor)

This project uses **Cursor subagents** so different tasks are handled by specialized agents. You can invoke them explicitly or let the main chat delegate when it recognizes the task type.

---

## Agents

| Agent | When to use | Invoke with |
|-------|-------------|-------------|
| **documentation-agent** | Extract learnings from a chat; update `docs/knowledge/`; write process docs or step-by-step guides | "Use the documentation-agent" then paste transcript or describe what to document |
| **scripting-agent** | Write or fix PowerShell; Dataverse/Azure DevOps API; scripts in Scripts/, Azure Setup/, Power Platform/ | "Use the scripting-agent" then describe the script task |
| **qa-agent** | Ask how we do something, where something is, or why we decided X | "Use the qa-agent" then ask your question |

---

## How to invoke

In any Cursor chat, say for example:

- **"Use the documentation-agent. [Then paste transcript or describe what to document.]"**
- **"Use the scripting-agent. [Then describe the script or fix you need.]"**
- **"Use the qa-agent. [Then ask your question.]"**

The main AI can also delegate on its own when your request clearly matches one of the descriptions above (see `.cursor/rules/orchestrator.mdc`).

---

## Orchestrator

There is no separate "orchestrator" process. The **default Cursor chat** acts as the orchestrator: it reads your message and either handles the task itself or **delegates to a subagent** based on the rules in `.cursor/rules/orchestrator.mdc`. In Cursor 2.4+, the main agent can **invoke subagents that run in the same chat** (they appear and work on screen without you opening another tab). For mixed tasks (e.g. "document this and then fix the script"), it will invoke the documentation agent then the scripting agent (or both) in one thread. If subagent invocation does not work in your Cursor version or environment, you can explicitly say "Use the documentation-agent" (etc.) and paste your request—see "How to invoke" above.

---

## Chat archive and knowledge

To turn past chats into lasting knowledge:

1. Copy the chat transcript (or save it to `archive/transcripts/`).
2. Open a new chat and say: **"Use the documentation-agent."** Then paste the transcript and ask it to extract knowledge into `docs/knowledge/` using the template in `docs/knowledge/README.md`.
3. Alternatively, use an external LLM with the prompt in `docs/knowledge/EXTRACTION_PROMPT.md` and save the output under `docs/knowledge/`.

Full process: **docs/processes/chat-archive-and-knowledge-extraction.md**.

---

## File locations

| What | Where |
|------|--------|
| Subagent definitions | `.cursor/agents/*.md` |
| Delegation rule | `.cursor/rules/orchestrator.mdc` |
| Knowledge notes | `docs/knowledge/YYYY-MM-DD_topic.md` |
| Process docs | `docs/processes/` |
| Archive process | `docs/processes/chat-archive-and-knowledge-extraction.md` |

---

## Worktrees (running agents in parallel)

Each agent role has its own worktree. Open the folder in Cursor to run that agent in a dedicated window:

| Agent | Worktree path | Branch |
|-------|---------------|--------|
| **documentation-agent** | `C:\Users\ddala\.cursor\worktrees\Cordea\documentation` | worktree-documentation |
| **scripting-agent** | `C:\Users\ddala\.cursor\worktrees\Cordea\scripting` | worktree-scripting |
| **qa-agent** | `C:\Users\ddala\.cursor\worktrees\Cordea\qa` | worktree-qa |
| General / orchestrator | `C:\Users\ddala\.cursor\worktrees\Cordea\bzf` | detached HEAD |

Full setup guide: **docs/Multi-Agent-Worktrees-Setup.md**.
