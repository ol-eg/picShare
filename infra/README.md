# picShare deployment (Ansible)

## Prerequisites (control machine — your dev box)

```bash
pip install ansible
ansible-galaxy collection install -r infra/requirements.yml
```

The server needs a fresh Debian install with SSH access.

## First-time setup

1. Edit `inventory.yml` — set your server IP and SSH user.

2. Copy secrets, then run:

```bash
ansible-playbook playbook.yml \
  --extra-vars "vault_db_password=<...> vault_secret_key=<...> vault_invite_code=<...>"
```

If registration is open (no invite code), set `vault_invite_code=""`.

3. Open `http://<server-ip>:8000` in a browser.

## Iterating (after first deploy)

After pulling new code on your dev machine, run again. Ansible is idempotent:

```bash
ansible-playbook playbook.yml
```

## Rolling back

```bash
ssh user@server
cd /opt/picshare
docker compose down
docker compose up -d    # previous images are still cached
# or rebuild with old tag
```