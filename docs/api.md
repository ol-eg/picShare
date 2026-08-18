# API Reference

The full interactive reference is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Both are auto-generated from the Python code — no manual sync needed.

---

## Endpoint overview (JSON API)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Create account, returns JWT. Body: `invite_code` (required if `PICSHARE_INVITE_CODE` is set) |
| POST | `/login` | No | Login, returns JWT |
| GET | `/me` | Yes | Current user info |
| POST | `/images` | Yes | Upload image (multipart) |
| GET | `/images` | No | List all images |
| PATCH | `/images/{id}` | Yes | Update caption (owner only) |
| DELETE | `/images/{id}` | Yes | Delete image (owner only) |

## Browser routes (form-based, cookie session)

These are the HTML routes the browser uses. They are excluded from the OpenAPI
schema (`include_in_schema=False`) and authenticate via an `httponly` cookie
named `picshare_session` (same signed JWT as Bearer auth), not the
`Authorization` header.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | Cookie optional | Home page; shows login/register or the signed-in user + logout |
| GET | `/register` | No | Render registration form |
| POST | `/register/form` | No | Register; on success sets the session cookie (auto-login) and redirects home |
| GET | `/login` | No | Render login form |
| POST | `/login/form` | No | Login; on success sets the session cookie and redirects home |
| POST | `/logout` | Cookie optional | Clears the session cookie and redirects home |

The session cookie is set with `HttpOnly` + `SameSite=lax`; it is *not* set with
`Secure`, so cookie sessions work over plain HTTP in dev (enable `secure` in
production).

## Static file URLs

- `GET /uploads/{filename}` — full-size uploaded image
- `GET /thumbnails/{filename}` — 300×300 thumbnail