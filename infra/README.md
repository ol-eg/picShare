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

Run from the repository root. The `infra/ansible.cfg` is picked up automatically because Ansible searches parent directories.

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

## Iterating

```bash
git pull
ansible-playbook infra/playbook.yml
```

Secrets are prompted again each time. The provisioning phase (Docker, firewall) is skipped on subsequent runs — it only acts if something is missing.

To change a secret later, just enter the new value when prompted — Ansible will rewrite `.env` and recreate containers.

## Notes

- The production compose file uses `restart: unless-stopped`, named volumes,
  and a Postgres healthcheck so the app waits for the DB.
- Default port is 8000. Change `app_port` via `--extra-vars "app_port=8080"`.