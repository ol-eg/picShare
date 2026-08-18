# picShare deployment (Ansible)

Run on the Debian server after cloning the repo.

## Prerequisites

```bash
sudo apt update
sudo apt install -y python3-pip ansible
ansible-galaxy collection install -r infra/requirements.yml
```

## Deploy

```bash
ansible-playbook infra/playbook.yml
```

Run from the repository root. The root-level `ansible.cfg` points Ansible to `infra/inventory.yml`.

## Result

After the playbook finishes you'll have two Docker containers running on the server:

| Container | Purpose |
|-----------|---------|
| `picshare-db-1`  | PostgreSQL 17 |
| `picshare-app-1` | FastAPI app on port **80** |

The app is reachable at **http://localhost** on the server itself.

### Firewall

The playbook enables **UFW** with a default-deny policy and explicitly allows:

- **SSH** — port `22` (configurable via the `ssh_port` play variable)
- the app — port `app_port` (default `80`)

SSH is allowed **before** UFW is enabled, so you never lock yourself out of the
box. If you lose SSH access anyway (e.g. you tweaked firewall rules by hand),
use your provider's out-of-band console (DigitalOcean Droplet Console, Vultr
VNC, Hetzner Console, …) and run:

```bash
sudo ufw allow 22/tcp
```

## Making it accessible from the internet

Your Debian server is on your home LAN (e.g. 192.168.0.X). To reach it from outside:

1. Log into your **router's admin panel** (usually http://192.168.0.1)
2. Find **Port Forwarding** (sometimes called "Virtual Server" or "NAT")
3. Add a rule:
   - **External port**: `80`
   - **Internal IP**: your server's LAN address (e.g. `192.168.0.50`)
   - **Internal port**: `80`
   - **Protocol**: TCP
4. Save and apply

Now you can access the app at **http://&lt;your-public-ip&gt;:8000** from anywhere.

To find your public IP: `curl ifconfig.me` on the server.

### DuckDNS (free hostname)

The playbook will prompt for a DuckDNS token on first deploy. If you provide
one, it installs a cron job that updates your DNS record every 5 minutes.
Your app is then reachable at **http://mypish.duckdns.org** (no port needed).

Get a free token at https://duckdns.org.

## Environment variables

The app reads configuration from environment variables (prefix `PICSHARE_`). On
the server these live in `/opt/picshare/.env`, created by the playbook.

| Variable | Default | Purpose |
|----------|---------|---------|
| `PICSHARE_DATABASE_URL` | — | SQLAlchemy async Postgres URL. Set by the playbook from the DB password. |
| `PICSHARE_SECRET_KEY` | `change-me-in-production` (insecure!) | Signs JWTs and the session cookie. **Required to be set** — the playbook prompts for it on first deploy. |
| `PICSHARE_INVITE_CODE` | unset | Registers are gated by this code. Empty = open registration. |
| `PICSHARE_COOKIE_SECURE` | `true` | Marks the `picshare_session` cookie `Secure`. Defaults `true`, **but the playbook writes `false` because the app currently serves over plain HTTP.** |
| `PICSHARE_THUMBNAIL_SIZE` | `300,300` | Thumbnail pixel size (power users only). |

> **Secure-cookie note (important).** Browsers ignore a `Secure` cookie over
> plain HTTP. This deployment serves the app over HTTP (port 80 /
> `http://mypish.duckdns.org`), so the playbook sets
> `PICSHARE_COOKIE_SECURE=false`. If you later put HTTPS/TLS in front, set it
> to `true` (or delete `/opt/picshare/.env` and re-run to answer prompts).

## Iterating

The simplest iteration — pull latest and re-deploy:

```bash
git pull
ansible-playbook infra/playbook.yml
```

The playbook rsyncs the source, rebuilds the image, and recreates the app
container automatically. No manual cleanup needed — the DB container stays
healthy and keeps all data.

### When code depends on a new env var (this is one!)

If a new release adds an env var the playbook doesn't already write, this
iteration does **not** re-prompt for secrets — it reads the existing
`/opt/picshare/.env` and appends the new variable only if the playbook knows
about it. In particular, this change added `PICSHARE_COOKIE_SECURE`; on an
existing server the playbook writes `false` (HTTP) unless the old `.env`
already set it. To change it later:

```bash
sudo sed -i 's/^PICSHARE_COOKIE_SECURE=.*/PICSHARE_COOKIE_SECURE=true/' /opt/picshare/.env
ansible-playbook infra/playbook.yml
```

### Full list of deploy env settable via prompts / .env

Secrets are only prompted on **first deploy**. On subsequent runs the playbook
reads existing values from `/opt/picshare/.env` and skips all prompts.

To change a secret later, delete the `.env` file first:

```bash
sudo rm /opt/picshare/.env
ansible-playbook infra/playbook.yml
```

If you need a full reset (e.g. DB schema changed):

```bash
sudo docker compose -f /opt/picshare/docker-compose.yml down --volumes
sudo rm /opt/picshare/.env
ansible-playbook infra/playbook.yml
```

## Notes

- The production compose file uses `restart: unless-stopped`, named volumes,
  and a Postgres healthcheck so the app waits for the DB.
- Default port is 8000. Change `app_port` via `--extra-vars "app_port=8080"`.