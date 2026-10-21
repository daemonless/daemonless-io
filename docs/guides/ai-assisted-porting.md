---
title: "AI-Assisted Porting: Using Coding Agents on Daemonless Images"
description: "How to use a coding agent on a daemonless image port: what the LLM policy requires, and the porting toolkit that provides the cookbook, build and CIT checks, and a pre-PR provenance audit."
---

# AI-Assisted Porting

Porting an upstream app to FreeBSD is repetitive, well-documented work with a
small number of recurring traps, which makes it a reasonable fit for a coding
agent.

This guide covers what the project requires of an AI-assisted contribution, and
the toolkit available to help meet it.

!!! warning "Read the policy first"
    The [LLM / AI Contribution Policy](llm-policy.md) applies to every
    repository in the Daemonless organization and governs everything on this
    page.

---

## What the policy requires

The full text is at [LLM / AI Contribution Policy](llm-policy.md). In short:

| Requirement | What it means for a port |
|---|---|
| **Understand what you commit** | You can explain why each non-obvious line exists — which error it fixes, or which upstream requirement it satisfies |
| **Test it first** | The image builds, CIT passes, and you have seen that happen. Untested output will have its PR closed |
| **Keep it clean** | No leftover AI artifacts, odd naming, or verbose generated comments |
| **Keep communication human** | PR descriptions, issues and review comments are in your own words |

The rest of this page is about tooling that helps with each of those.

---

## The porting toolkit

The [porting toolkit](https://github.com/daemonless/porting-toolkit) collects the
shared procedure and accumulated knowledge behind daemonless ports. It is
optional — a hand-written port is perfectly welcome.

The procedure, cookbook and checks are plain markdown and POSIX shell, so they
are not tied to one assistant. Per-agent integration is an optional adapter.
Claude Code is the only agent the toolkit has been run with so far and the only
one with an adapter; others should work but are untested.

### Install it

```bash { linenums="0" }
git clone https://github.com/daemonless/porting-toolkit
cd <your-image-repo>
../porting-toolkit/install.sh              # with an agent adapter
../porting-toolkit/install.sh --agent none # neutral files and git hooks only
```

That adds four things to the image repo:

| Path | What it is |
|---|---|
| `.porting/` | The procedure, the cookbook, three fresh-context prompts, and templates |
| `scripts/` | `build.sh`, `cit-with-logs.sh`, `lint-compose.sh` |
| `.git/hooks/pre-push` | Refuses a push without a passing CIT |
| `AGENTS.md` | The per-image entry point your agent reads first |

!!! tip "Name the directory after the image"
    `dbuild` derives the image name from the working directory and has no
    override, so a fork checked out as `<app>-daemonless` builds an image called
    `<app>-daemonless` — in the README, the registry refs and the built tag.
    Rename the directory before you start. `install.sh` warns about it and
    `lint-compose.sh` fails on it.

### The cookbook

`.porting/cookbook.md` is keyed by **error signature**: paste the literal line
your build printed into `grep -F` and get a build-verified fix, its cause and
the rationale. It covers things like FreeBSD's `node26` shipping without the
TC39 `Temporal` global, `libsql` having no FreeBSD native build, and the
podman-on-ZFS layer-commit stall that looks like a hang but isn't.

The procedure makes a cookbook lookup the first action on any error, before
hypothesising — a model that greps a verified cookbook gives a better answer
than one reasoning from scratch about an unfamiliar platform.

### Contributing back to the cookbook

When you solve something the cookbook doesn't cover, append an entry and open a
PR against the toolkit. Each entry is signature, cause, fix, and why. Entries
must be build-verified — one you haven't seen work belongs in the PR discussion
instead. That loop is what keeps the next port fast.

---

## Checks the toolkit adds

### Automated checks

These are ordinary programs, so they behave the same whichever agent — or
human — drives the repo:

| Check | Fails on |
|---|---|
| `scripts/build.sh` | a stale `Containerfile`; a build log containing failure signatures despite `dbuild build` exiting 0 |
| `scripts/cit-with-logs.sh` | marking the port green unless CIT **and** the smoke test both pass |
| `scripts/lint-compose.sh` | a directory name that doesn't match the image name, metadata mismatches, an unpinned upstream ref, an unguarded patch, a build toolchain in the runtime stage |
| `.git/hooks/pre-push` | any push without a `.cit-passed` marker |

### Functional smoke test

CIT confirms a process listens; it does not confirm the app works. Each port
writes a `scripts/smoke-test.sh` making one request that exercises the app's
actual purpose against the freshly built image. The `.cit-passed` marker is only
written when CIT and the smoke test both pass.

### Provenance audit before the PR

The toolkit runs a `port-auditor` pass in a fresh context before any PR. It
walks every non-boilerplate line in `Containerfile.j2`, the run scripts and each
patch and asks whether it traces to the port brief, a cookbook entry, or a
logged error. A line with no source is a finding: it gets documented, or removed
and the build re-proven without it.

It also reports what breaks first on the next upstream bump, and whether that
failure would be loud or silent.

### The human opens the PR

The agent produces the branch, the build evidence, `BUILD-NOTES.md`, a
`PROCESS-LOG.md` of what broke and what fixed it, and the audit verdict — then
stops. It does **not** write the PR description: the policy does not allow
AI-generated text there. You write it yourself from that evidence.
`.porting/templates/PR-BODY.md` is an outline of what to cover, not prose to
paste.

It asks you to answer three questions in your own words:

- Why this base and runtime, and not the obvious alternative?
- What is the riskiest dependency or assumption in this image?
- What breaks first on the next upstream bump, and would it fail loud or silent?

---

## For reviewers

Useful artefacts to ask for on any port, agent-assisted or not:

- **`BUILD-NOTES.md`** — every FreeBSD-specific change with its reason. Check
  that each listed change exists in the diff, and each change in the diff is
  listed.
- **`PROCESS-LOG.md`** — what broke and what fixed it, per phase.
- **The Viva answers** — three specific sentences from someone who did the port.

---

## Need help?

Join the [Discord](https://discord.gg/Kb9tkhecZT). Asking "my build dies with
this signature, is there a known fix?" is usually faster than guessing, and the
answer often becomes a cookbook entry.
