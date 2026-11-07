---
title: "AI-Assisted Porting: Using Coding Agents on Daemonless Images"
description: "How to use a coding agent on a daemonless image port: what the LLM policy requires, and the porting toolkit that provides the cookbook, build and CIT checks, and a pre-PR provenance audit."
---

# AI-Assisted Porting

Adding new containers to the Daemonless fleet is a reasonably good fit for a coding agent, as scaffolding is well-structured, it can rely on dbuild for building & testing, and built-in functions take care of required files like README and container files.

The goal of this toolkit is to pull in the right context and checkpoints, avoid common mistakes, and includes a record of previous patches that the agent can refer to. 

This guide also covers what the project requires of an AI-assisted contribution, so you can port the apps over that you want, while doing so in a way that makes it easy for everyone including reviewers.

!!! warning "Read the policy first"
    The [LLM / AI Contribution Policy](llm-policy.md) applies to every
    repository in the Daemonless organization and governs everything on this
    page.

---

## What the policy requires

In short:

| Requirement | What it means for a port |
|---|---|
| **Understand what you commit** | You can explain why each non-obvious line exists: which error it fixes, or which upstream requirement it satisfies |
| **Test it first** | The image builds, CIT passes, and you have seen that happen. Untested output will have its PR closed |
| **Keep it clean** | No leftover AI artifacts, odd naming, or verbose generated comments |
| **Keep communication human** | PR descriptions, issues and review comments are in your own words |

The rest of this page is about tooling that helps with each of those.

---

## The porting toolkit

The [porting toolkit](https://github.com/daemonless/porting-toolkit) holds the
porting procedure, a cookbook of build-verified fixes, and the checks below. It
is optional. Hand-written ports are welcome.

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
    `<app>-daemonless`, and that name ends up in the README, the registry refs
    and the built tag.
    Rename the directory before you start. `install.sh` warns about it and
    `lint-compose.sh` fails on it.

### The cookbook

`.porting/cookbook.md` is keyed by **error signature**: paste the literal line
your build printed into `grep -F` and get a build-verified fix, its cause and
the rationale. It covers things like FreeBSD's `node26` shipping without the
TC39 `Temporal` global, `libsql` having no FreeBSD native build, and the
podman-on-ZFS layer-commit stall that looks like a hang but isn't.

The procedure makes a cookbook lookup the first step on any error, before the
agent starts guessing at causes.

### Contributing back to the cookbook

When you solve something the cookbook doesn't cover, append an entry and open a
PR against the toolkit. Each entry is signature, cause, fix, and why. Entries
must be build-verified. One you haven't seen work belongs in the PR discussion
instead.

---

## Checks the toolkit adds

### Automated checks

These are ordinary scripts, so they behave the same whoever runs them:

| Check | Fails on |
|---|---|
| `scripts/build.sh` | a stale `Containerfile`; a build log containing failure signatures despite `dbuild build` exiting 0 |
| `scripts/cit-with-logs.sh` | CIT or the smoke test failing. It writes `.cit-passed` only when both pass |
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
`PROCESS-LOG.md` of what broke and what fixed it, and the audit verdict. Then it
stops. It does **not** write the PR description, because the policy forbids
AI-generated text there. You write it from that evidence.
`.porting/templates/PR-BODY.md` lists what to cover. It is not prose to paste.

The template asks you to answer three questions in your own words:

- Why this base and runtime, and not the obvious alternative?
- What is the riskiest dependency or assumption in this image?
- What breaks first on the next upstream bump, and would it fail loud or silent?

---

## For reviewers

On a toolkit port, ask for:

- **`BUILD-NOTES.md`** — every FreeBSD-specific change with its reason. Check
  that each listed change exists in the diff, and each change in the diff is
  listed.
- **`PROCESS-LOG.md`** — what broke and what fixed it, per phase.
- **Answers to the three questions above**, in the submitter's own words.

---

## Need help?

Join the [Discord](https://discord.gg/Kb9tkhecZT).
