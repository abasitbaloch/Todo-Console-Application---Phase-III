---
id: 002
title: Phase II Constitution Update
stage: constitution
date: 2026-01-07
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: abasitbaloch
command: /sp.constitution
labels: ["constitution", "phase-ii", "full-stack", "architecture"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

```text
Project: Phase II - Todo Full-Stack Web Application (The Evolution of Todo)

Core principles:
- [cite_start]**Spec-Driven Absolutism**: No line of code is written without a corresponding Task ID from `speckit.tasks`.
- **User Isolation**: Absolute data privacy. [cite_start]A user must NEVER be able to query another user's data. [cite: 169]
- **Monorepo Separation**: Clear boundary between Client (Frontend) and Server (Backend).
- **Stateless Architecture**: The backend relies entirely on JWT tokens for context, storing no session state in memory.

Key standards:
- **Frontend**: Next.js 16+ (App Router), TypeScript (Strict), Tailwind CSS (Modern SaaS Aesthetic).
- **Backend**: Python 3.13+, FastAPI, SQLModel, Pydantic (Strict Schemas).
- **Database**: Neon Serverless PostgreSQL.
- **Auth**: Better Auth (Frontend) issues JWTs; [cite_start]Backend verifies them using a SHARED SECRET. [cite: 165-167]
- **API**: RESTful endpoints. All responses must be typed JSON.

Constraints:
- **Folder Structure**: `/frontend`, `/backend`, `/specs`, `/.spec-kit`.
- [cite_start]**Reference Rule**: Every commit or code generation must reference the Task ID (e.g., "Implementing T-001"). [cite: 1029]
- **Visual Design**: Polished, professional UI. Use `lucide-react` for icons and consistent spacing.
- [cite_start]**Security**: All API routes (except `/health` and `/auth/*`) must verify the `Authorization: Bearer <token>` header. [cite: 172]

Success criteria:
- **Auth Handshake**: Frontend successfully passes JWT to Backend, and Backend successfully decodes user_id.
- **Persistence**: Tasks survive a server restart [truncated]
```

## Response snapshot

Updated constitution from v1.0.0 (Phase I - CLI) to v2.0.0 (Phase II - Full-Stack Web Application).

**Major Changes**:
- Replaced "Spec-First Development" with "Spec-Driven Absolutism" (strengthened with Task ID requirement)
- Removed "Deterministic Behavior" principle (not applicable to stateful web apps)
- Replaced "CLI-First Interface" with web interface requirements
- Redefined "Separation of Concerns" as "Monorepo Separation" (client/server architecture)
- Added three new principles: User Isolation, Stateless Architecture, Security First
- Complete technology stack replacement: Python CLI → Next.js + FastAPI + PostgreSQL
- Updated constraints: persistence and multi-user support now in scope

**Version Bump Rationale**: MAJOR (1.0.0 → 2.0.0) due to breaking architectural changes, complete technology stack replacement, and fundamental shift from in-memory CLI to persistent full-stack web application.

**Template Consistency**: Verified alignment with plan-template.md, spec-template.md, and tasks-template.md. All templates support the new monorepo structure and web application requirements.

## Outcome

- ✅ Impact: Constitution updated to Phase II requirements with 9 core principles (7 new/modified, 2 retained)
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (complete rewrite)
- 🔁 Next prompts: Create feature specification for Phase II implementation, run /sp.specify
- 🧠 Reflection: Major version bump appropriate given architectural paradigm shift. User input was truncated but context was sufficient to infer complete requirements.

## Evaluation notes (flywheel)

- Failure modes observed: None. User input truncation handled by inferring "restart" from "resta".
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, version incremented correctly, sync impact report complete)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Consider adding principle for API versioning strategy if breaking changes become frequent in Phase II development
