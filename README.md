# Vrika Admin Portal

Internal license administration portal for the Vrika/CipherStrike cybersecurity platform.

**Architecture:** This admin server runs in the cloud. It manages and generates licenses that are deployed to on-premise vrika-server installations. Each has its own database and JWT secret — they are completely independent.

## Structure

```
vrika-admin/
├── frontend/          # Next.js admin UI (port 4001)
├── backend/           # FastAPI admin API (port 4000)
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
| POST | /license-admin/machine-info/hash | Hash machine info |

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
