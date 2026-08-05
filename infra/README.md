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
| `picshare-app-1` | FastAPI app on port **8000** |

The app is reachable at **http://localhost:8000** on the server itself.

## Making it accessible from the internet

Your Debian server is on your home LAN (e.g. 192.168.0.X). To reach it from outside:

1. Log into your **router's admin panel** (usually http://192.168.0.1)
2. Find **Port Forwarding** (sometimes called "Virtual Server" or "NAT")
3. Add a rule:
   - **External port**: `8000`
   - **Internal IP**: your server's LAN address (e.g. `192.168.0.50`)
   - **Internal port**: `8000`
   - **Protocol**: TCP
4. Save and apply

Now you can access the app at **http://&lt;your-public-ip&gt;:8000** from anywhere.

To find your public IP: `curl ifconfig.me` on the server.

### DuckDNS (free hostname)

The playbook will prompt for a DuckDNS token on first deploy. If you provide
one, it installs a cron job that updates your DNS record every 5 minutes.
Your app is then reachable at **http://mypish.duckdns.org:8000** regardless
of IP changes.

Get a free token at https://duckdns.org.

## Iterating

```bash
git pull
ansible-playbook infra/playbook.yml
```

The playbook rsyncs the source, rebuilds the image, and recreates the app
container automatically. No manual cleanup needed — the DB container stays
healthy and keeps all data.

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