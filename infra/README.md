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
ansible-playbook infra/playbook.yml \
  --extra-vars "vault_db_password=<...> vault_secret_key=<...> vault_invite_code=<...>"
```

If registration is open (no invite code), set `vault_invite_code=""`.

## Iterating

```bash
git pull
ansible-playbook infra/playbook.yml
```

The provisioning phase (Docker, firewall) is skipped on subsequent runs — it only acts if something is missing.

## Notes

- The production compose file uses `restart: unless-stopped`, named volumes,
  and a Postgres healthcheck so the app waits for the DB.
- Default port is 8000. Change `app_port` via `--extra-vars "app_port=8080"`.