# API Reference

The full interactive reference is available at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Both are auto-generated from the Python code — no manual sync needed.

---

## Endpoint overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Create account, returns JWT |
| POST | `/login` | No | Login, returns JWT |
| GET | `/me` | Yes | Current user info |
| POST | `/images` | Yes | Upload image (multipart) |
| GET | `/images` | No | List all images |
| PATCH | `/images/{id}` | Yes | Update caption (owner only) |
| DELETE | `/images/{id}` | Yes | Delete image (owner only) |

## Static file URLs

- `GET /uploads/{filename}` — full-size uploaded image
- `GET /thumbnails/{filename}` — 300×300 thumbnail