---
description: Investigate a production issue step-by-step, with the user involved
agent: code
---

The user wants to investigate a production problem together, in a slow,
deliberate loop. Follow this protocol exactly.

## Our agreed way of working (the contract)

- Do NOT rush. Do NOT guess. We move one evidence-gathering step at a time.
- **I suggest a command I think will give a clue. The user runs it themselves
  (never assume I can run prod commands) and pastes back the output plus their
  own read of it.**
- I interpret their output, form a hypothesis, and suggest the NEXT command.
- We repeat this loop until we find the root cause. Only then does discussion
  of a fix begin, and fixes follow TDD (per AGENTS.md).
- The user is a novice: explain commands plainly, say WHY a command helps
  before asking them to run it.

## Why we can't just write a failing test first here

We can still "write a failing test once we know the cause", but we can't write
a meaningful test until we understand the bug — so investigation precedes
RED/GREEN. Tests existing and passing in dev is usually the clue: prod is
missing something dev has, so hunt the dev/prod delta.

## Concrete investigation checklist (start here, in order)

1. **Errors/logs first.** Get the app container's logs around the failure:
   `sudo docker logs --tail 100 picshare-app-1` (adjust container name).
   Look for Traceback / exception type / failing line / env-file context.
2. **Identify the failing layer** from the traceback (route handler, a
   dependency like `get_current_user`, service, repository, DB, or a middleware).
3. **Reproduce in isolation / compare dev vs prod:** check whether the config
   driving the code path (env vars set by the Ansible `.env`, compose template,
   DB state, image build) differs between dev and prod. Prod config lives in
   `/opt/picshare/.env` and `/opt/picshare/docker-compose.yml` (generated from
   `infra/docker-compose.yml.j2`).
4. **Contain the blast radius:** isolate whether it's one endpoint, one user,
   all auth, or just this box — before proposing any change.

Keep the loop tight: one command → output → interpretation → next command.
Resist the urge to jump ahead to a fix.