---
date: 2026-05-10
topic: "MCUB OpenAgent Skills Plugin"
status: validated
---

## Problem Statement

We need a dedicated **MCUB OpenAgent skills plugin** that captures the project-specific workflows we already use for MCUB development, debugging, module creation, and release preparation.

Right now the knowledge exists across `.opencode/skills`, exported `openagent_skills`, debugger conventions, and the OpenAgent skill registry. The plugin should make that workflow reusable from OpenAgent without confusing MCUB modules with Hikka-style modules.

## Constraints

The plugin must stay compatible with the existing OpenAgent skill system in `OpenAgent-MCUB-repo.py`.

**Non-negotiables:**

- Use the current `.opencode/skills/<skill-name>/SKILL.md` structure.
- Include YAML frontmatter with `name` and `description`.
- Keep guidance MCUB-specific, not Hikka-specific.
- Use existing OpenAgent skill registry behavior instead of inventing a new registry.
- Support export/import into the existing `openagent_skills` markdown format.
- Avoid changing debugger behavior as part of this plugin design.

## Approach

I’m choosing a **single workflow-oriented skill plugin** first, rather than splitting this into multiple smaller skills immediately.

The first skill should act as the OpenAgent entry point for MCUB work: it routes the model toward the right existing workflows, references the current MCUB module creation/release skills, and explains how to use the OpenAgent skill tools safely.

**Why this is the right first step:**

- It gives OpenAgent one obvious MCUB workflow skill to load.
- It avoids duplicating all content from existing specialized skills.
- It keeps the initial plugin easy to validate.
- It leaves room to split into agents or more focused skills later.

I considered creating separate skills for debugger fixing, module creation, release publishing, and OpenAgent commands. I’m rejecting that for now because we already have focused MCUB skills, and the missing piece is a **cohesive OpenAgent workflow layer**.

## Architecture

The design adds one new local skill under `.opencode/skills`, with an optional exported copy under `openagent_skills`.

**Local source of truth:**

- `.opencode/skills/MCUB-openagent-workflow/SKILL.md`

**Optional exported form:**

- `openagent_skills/MCUB-openagent-workflow.md`

The local skill is the authoritative editable version. The exported markdown is only a compatibility artifact for OpenAgent import/export workflows.

## Components

**Skill frontmatter:** Defines the skill name and concise trigger description so OpenAgent can list and load it predictably.

**Usage triggers:** Explains when the skill should be used, especially for MCUB repo navigation, debugger work, module creation, release work, and OpenAgent skill management.

**Repository orientation:** Points the agent to the relevant MCUB concepts and directories without duplicating the whole codebase map.

**Workflow routing:** Tells the agent when to use existing specialized skills:

- `MCUB-modules-creator` for creating or updating debug modules.
- `MCUB-release-modules` for validating and publishing modules.
- Debugger workflow guidance for lint/rule/test work.
- OpenAgent skill registry guidance for listing, reading, importing, exporting, and saving skills.

**Safety rules:** Captures important project constraints, especially avoiding Hikka APIs, avoiding accidental secret exposure, and preserving existing debugger expectations.

## Data Flow

The workflow starts when OpenAgent receives a MCUB-related task and loads the new skill.

**Expected flow:**

- User asks for MCUB-related work.
- OpenAgent loads `MCUB-openagent-workflow`.
- The skill classifies the work as module creation, release, debugging, skill management, or general repo guidance.
- The skill routes to the right existing skill or workflow.
- If skill files need to move between local and exported formats, OpenAgent uses its existing skill registry tools.

This keeps OpenAgent’s existing registry as the source of operational behavior while the new skill provides project-specific judgment.

## Error Handling

The skill should bias toward safe recovery instead of guessing.

**Registry mismatch:** If a skill exists locally but not in exported form, treat the local `.opencode/skills` version as authoritative and export only when needed.

**Missing skill file:** If an expected specialized skill is missing, continue with the workflow guidance from the OpenAgent workflow skill and report the missing dependency.

**Ambiguous module style:** If a module appears Hikka-style, stop that path and redirect to MCUB class-style module conventions.

**Debugger failures:** Use the debugger tests and targeted rule validation as the verification path rather than broad unrelated rewrites.

## Testing Strategy

Verification should be lightweight and focused because this is a documentation/configuration-style plugin.

**Checks:**

- Confirm the new skill appears under `.opencode/skills/<name>/SKILL.md`.
- Confirm frontmatter contains valid `name` and `description` fields.
- Confirm the first line/metadata is compatible with OpenAgent skill listing behavior.
- Confirm the skill mentions and routes to existing MCUB specialized skills.
- Confirm exported markdown can exist in `openagent_skills` without becoming the source of truth.

**Manual validation:**

- Ask OpenAgent to list skills.
- Ask OpenAgent to read the new skill.
- Ask OpenAgent to handle one MCUB module task and one debugger task using the workflow routing.

## Open Questions

There are no blocking open questions.

The only future decision is whether to split this workflow skill into multiple OpenAgent agents later. I’m intentionally deferring that until the skill plugin proves useful in normal MCUB work.
