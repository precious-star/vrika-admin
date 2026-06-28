# Vrika Admin Portal

Internal license administration portal for the Vrika/CipherStrike cybersecurity platform.

**Architecture:** This admin server runs in the cloud. It manages and generates licenses that are deployed to on-premise vrika-server installations. Each has its own database and JWT secret — they are completely independent.

## Structure

```
vrika-admin/
├── frontend/          # Next.js admin UI (port 4001)
├── backend/           # FastAPI admin API (port 4000)
├── scripts/           # Client-side utility scripts
└── docker-compose.yml # Full-stack deployment
```

## Quick Start

```bash
# 1. Copy env files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# 2. Generate a JWT secret
openssl rand -hex 32
# Paste the output as JWT_SECRET in backend/.env

# 3. Generate license signing keys (ECDSA P-256)
mkdir -p backend/keys
openssl ecparam -genkey -name prime256v1 -noout -out backend/keys/license_private.pem
openssl ec -in backend/keys/license_private.pem -pubout -out backend/keys/license_public.pem

# 4. Start all services
docker compose up -d

# Admin UI: http://localhost:4001
# Admin API: http://localhost:4000
```

## Create Admin User

```bash
docker compose exec admin-api python -m app.scripts.create_admin \
  --email admin@example.com \
  --password secret123 \
  --username "Admin" \
  --org "Vrika"
```

## Database

The admin portal uses its own MongoDB instance (runs as `admin-mongo` container). It stores:
- `users` — admin portal users
- `organizations` — admin organizations
- `licenses` — generated license records
- `license_customers` — customer registry
- `machine_infos` — stored machine hardware info per customer
- `license_activity` — audit log

## Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/login | Admin login |
| GET | /auth/me | Current user info |
| GET | /license-admin/dashboard | Dashboard stats |
| GET | /license-admin/customers | List customers |
| POST | /license-admin/customers | Create customer |
| POST | /license-admin/licenses/generate | Generate license |
| GET | /license-admin/licenses | List all licenses |
| GET | /license-admin/licenses/:id/download | Download license file |
| POST | /license-admin/licenses/:id/revoke | Revoke license |
| GET | /license-admin/available-tools | List available tools |
| POST | /license-admin/customers/:id/machine-info | Submit machine info for customer |
| GET | /license-admin/customers/:id/machine-info | List machine infos for customer |
| DELETE | /license-admin/customers/:id/machine-info/:mid | Delete a machine info entry |

## Frontend Pages

| Route | Description |
|-------|-------------|
| /login | Admin authentication |
| /dashboard | Overview stats |
| /customers | Customer management |
| /licenses/generate | Generate new license |
| /licenses/manage | View/revoke/download licenses |

## Security

- Independent JWT auth (separate secret from on-prem vrika-server)
- Only `license_admin` or `tenant_admin` roles can access
- Private signing key never leaves this server
- ECDSA P-256 signatures for license integrity
- Generated licenses are deployed to on-prem servers as `.key` files

## Collect Machine Info (Client Script)

Run this script on the customer's machine to collect hardware info and push it to the admin portal. Requires only Python 3.7+ (no extra dependencies).

### Usage

```bash
python3 scripts/collect_machine_info.py \
    --customer-id <CUSTOMER_ID> \
    --api-url <ADMIN_API_URL> \
    --token <JWT_TOKEN>
```

### Example

```bash
python3 scripts/collect_machine_info.py \
    --customer-id 683ff1a2b3c4d5e6f7890abc \
    --api-url http://192.168.1.100:4000 \
    --token eyJhbGciOiJIUzI1NiIs...
```

### Where to get each value

| Param | How to get |
|-------|------------|
| `--customer-id` | Go to **Customers** page → click **Copy ID** button next to the customer |
| `--api-url` | Your backend URL — port `4000` for direct API, or port `4001/be` via frontend proxy |
| `--token` | JWT token from admin login (browser DevTools → Local Storage or Network tab `Authorization` header) |

### Options

| Flag | Description |
|------|-------------|
| `--save-local` | Also save a `machine-info.json` file locally on the client machine |

### What it collects

The script auto-detects the OS (Linux, macOS, Windows) and collects:

- Machine ID
- BIOS UUID
- CPU vendor, model, family
- Disk serial number
- Hostname
- MAC address

At least 3 of these must be available to generate a valid fingerprint. The collected info is pushed to the admin portal and stored under the customer. When generating a license, you select the stored machine info from a dropdown instead of uploading a file.
