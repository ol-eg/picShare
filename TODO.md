# TODO

Tracked items for future sessions. We practice small, incremental steps here.

## Full browser auth (auto-login + working login/logout) ✅ DONE

**Decided 2026-08-14, completed 2026-08-18.** Previously the frontend had no
auth mechanism — Bearer-only API auth, `/login` a bare stub, no cookie/token
storage. Implemented httponly-cookie browser auth alongside the (untouched)
Bearer API auth. Done in 6 small TDD steps, each verified with `make test` /
`make lint` / `make typecheck`.

- ✅ `POST /register/form` sets the session cookie (auto-login on register)
- ✅ `POST /login/form` sets the session cookie on success, error otherwise
- ✅ `POST /logout` clears the cookie
- ✅ `home.html` reflects logged-in state (username + logout vs login/register)

Cookie helpers in `app/auth.py`: `SESSION_COOKIE`, `create_session_cookie`,
`read_session_cookie`, and the `get_current_user_from_cookie` dependency. Cookie
value is the same signed JWT used by Bearer auth.

## Architectural refactor: Decouple `main.py` from the database ✅ DONE

**Goal:** remove direct DB access from `main.py` so handlers become thin
HTTP-routing-only code. Auth + images move to repository/service layers,
matching the Module Coupling diagram.

**Approach:** full repository + service layer, done in small sub-steps — auth
first, then images. `main.py` is now fully clean of direct DB access.

### Principles
- TDD: write a failing test first, confirm RED, then the minimal code for GREEN.
- Small steps, keep `make test` / `make lint` / `make typecheck` green throughout.
- Preserve existing API contracts exactly (existing tests pass without edits).

### Step 1 — Auth service + repositories ✅ DONE
- `repositories.py` with `UserRepository`.
- `services.py` — `register_user` / `login_user` with domain exceptions.
- Rewrote `POST /register`, `POST /register/form`, and `POST /login` to delegate.
- Updated the Module Coupling diagram for the repository/service layers.

### Step 2 — Images ✅ DONE
- Added `ImageRepository` and image services (`upload`, `list`, `update`, `delete`).
- Rewrote the four image endpoints to delegate — `main.py` no longer touches the DB.

## Backlog

Items we should address in a future session, captured from code reviews and
deferred decisions. Each has a short "why" for context. Not currently blocking.

- **Set `secure=True` on the session cookie.** ✅ DONE — now configurable via
  `PICSHARE_COOKIE_SECURE` (defaults `true` in code; dev and prod compose files
  set `false` because the app currently serves over plain HTTP). Flip the
  compose `.env` value to `true` once HTTPS/TLS is in front of the app.
- **Add a distinct `exp` to session tokens.** `create_token` produces a
  non-expiring JWT used for both Bearer and cookie auth. A never-expiring login
  cookie is a stale-session risk; consider a short-lived session token or a
  server-side expiry. Deferred as a design decision.
- **Logout UX polish.** Logout is a POST form (correct — state change), but a
  graceful button (e.g. htmx POST) reads better than a bare form link.
- **Upload hardening.** Validate `content_type` (whitelist `image/*`) and add a
  file-size cap before `save_upload`. Currently any file type/any size is
  accepted. Raised in local code review (Step 2).
- **Move Pillow/image I/O off the event loop.** `save_upload` does synchronous
  disk writes + CPU-bound Pillow thumbnail work inside the async path. Offload
  via `asyncio.to_thread` (or `aiofiles`). Raised in local code review (Step 2).
- **Decide whether `GET /images` should require auth.** It's currently public
  and `ImageOut` exposes `owner_id`, enabling user enumeration. Either gate it
  or omit `owner_id` from the public response. Raised in local code review
  (Step 2).
- **Add `max_length` on image captions.** `ImageUpdate.caption` has no length
  limit and the DB column is unbounded `Text` — a DoS vector for large
  captions. Raised in local code review (Step 2).
- **Handle delete leaving files on disk.** `delete_image` removes the DB row
  but not the uploaded file/thumbnail on disk. Confirm intended, then either
  document it or clean up files on delete.
- **Consider `expire_on_commit` / relationship loading.** Production sessions
  use the SQLAlchemy default `expire_on_commit=True`; if any route later
  traverses `image.owner`, avoid an implicit lazy-load N+1. Not an issue today.
- **Registration TOCTOU.** `register_user` checks username then inserts;
  the DB unique constraint is the safety net. Catch `IntegrityError` and map
  to a clean `409` under high concurrency rather than a raw failure. Raised in
  local code review (Step 2).