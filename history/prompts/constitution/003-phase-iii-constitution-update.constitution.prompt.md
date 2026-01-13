---
id: 003
title: Phase III Constitution Update
stage: constitution
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp", "openai-agents", "architectural-evolution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

**Project:** Phase III — AI-Powered Todo Chatbot (The Evolution of Todo)

**Core Principles:**
* **Spec-Driven Execution:** No agent is allowed to write code until the specification is complete and approved.
* **Stateless Intelligence:** The backend server must remain strictly stateless; all conversation history and application state must be persisted to the database.
* **Architectural Decoupling:** AI logic must be separated from task execution using the Model Context Protocol (MCP) server architecture.
* **Safety & Confirmation:** The agent must always confirm actions with a friendly response and handle destructive actions (delete/update) gracefully.

**Key Standards:**
* **AI Framework:** All conversational and agentic logic must be implemented using the **OpenAI Agents SDK**.
* **Protocol Standard:** Tool communication must use the **Official MCP SDK** to expose task operations as tools.
* **Authentication:** Every API request must include a valid **JWT token** and enforce user isolation.
* **Data Integrity:** Database models for Tasks, Conversations, and Messages must be strictly linked to a `user_id` to filter and return only user-specific data.
* **Clean Code:** Follow clean code principles and the established Python project structure from Phase I.

**How the Chatbot Works:**
* [User input was truncated at "Rite: 1057, 1059]." - assumed to describe chatbot interaction flow]

## Response snapshot

Updated constitution from version 2.0.0 (Phase II - Web App) to version 3.0.0 (Phase III - AI-Powered Chatbot).

**Major Changes (MAJOR version bump):**
1. **Modified Principles:**
   - Stateless Architecture → Stateless Intelligence (clarified: backend stateless, database persists conversations and messages)
   - Technology Stack → Complete expansion (added OpenAI Agents SDK, MCP SDK)

2. **Added Principles:**
   - IV. Architectural Decoupling (AI logic separated via MCP server architecture)
   - V. Safety & Confirmation (agent must confirm actions with friendly responses)

3. **Retained Principles:**
   - I. Spec-Driven Absolutism (unchanged)
   - II. User Isolation (unchanged)
   - VI. Monorepo Separation (unchanged)
   - VII. AI-Generated Code Only (unchanged)
   - VIII. Simplicity and Clarity (unchanged)
   - IX. Security First (enhanced with OpenAI API key security)

4. **Technology Stack Expansion:**
   - Backend: Added OpenAI Agents SDK for conversational AI
   - Backend: Added Official MCP SDK for tool communication
   - Database: Added tables for conversations and messages
   - Frontend: Added chat interface components

5. **Development Workflow Updates:**
   - Planning Phase: Added MCP tool schema definitions
   - Implementation Phase: Added MCP tools and AI agent logic implementation
   - Validation Phase: Added conversational flow testing
   - Documentation Phase: Added MCP tool schema documentation

6. **Constraints Updates:**
   - In Scope: Added conversational AI chatbot, natural language task management, MCP server architecture, conversation/message persistence
   - Out of Scope: Added advanced AI features, multi-agent orchestration
   - Non-Negotiable: Added OpenAI Agents SDK, MCP SDK, stateless backend requirement, MCP tools for all task operations

**Sync Impact Report Created:**
- Templates validated: plan-template.md, spec-template.md, tasks-template.md all align with new principles
- Pending updates: README.md (Phase III setup), CLAUDE.md (AI agent development guidance)
- Follow-up TODOs: Document OpenAI API configuration, MCP server setup, conversation persistence strategy

**Version Bump Rationale:**
MAJOR (2.0.0 → 3.0.0) because this introduces breaking architectural changes:
- New AI agent layer with OpenAI Agents SDK
- New MCP server architecture for tool communication
- New database schema (conversations, messages tables)
- New development patterns (AI orchestration, tool definitions)
- Fundamental shift from traditional web app to AI-powered conversational interface

## Outcome

- ✅ Impact: Constitution successfully updated to Phase III with 2 new principles (Architectural Decoupling, Safety & Confirmation), expanded technology stack (OpenAI Agents SDK, MCP SDK), and comprehensive constraints for AI-powered chatbot development
- 🧪 Tests: No tests required for constitution updates
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify (create Phase III feature specification), update README.md with Phase III setup instructions, update CLAUDE.md with AI agent development guidance
- 🧠 Reflection: The constitution evolution from Phase I (CLI) → Phase II (Web App) → Phase III (AI Chatbot) demonstrates progressive architectural sophistication while maintaining core principles (Spec-Driven, User Isolation, AI-Generated Code). The addition of MCP architecture and Safety & Confirmation principles addresses the unique challenges of conversational AI interfaces.

## Evaluation notes (flywheel)

- Failure modes observed: None - constitution update completed successfully with all placeholders filled and sync impact report generated
- Graders run and results (PASS/FAIL): PASS - No unresolved placeholders, version incremented correctly (MAJOR bump justified), dates in ISO format, principles declarative and testable, templates validated for consistency
- Prompt variant (if applicable): Standard /sp.constitution command execution
- Next experiment (smallest change to try): Consider creating an ADR for the MCP architecture decision (significant architectural choice with multiple alternatives: direct AI-to-DB vs MCP tools vs service layer)
