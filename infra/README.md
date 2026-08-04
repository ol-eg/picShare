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

You'll be prompted for:
- **Postgres password** — any strong password
- **Secret key** — used to sign login tokens (JWT). Paste the output of `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Without this, anyone can forge auth tokens.
- **Invite code** — optional, press Enter for open registration

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