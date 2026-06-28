# Vrika Admin Portal

Internal license administration portal for the Vrika/CipherStrike cybersecurity platform.

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

# 2. Add license signing keys
mkdir -p backend/keys
# Copy license_private.pem and license_public.pem to backend/keys/

# 3. Start all services
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

## Shared Database

Both `vrika-server` (main product) and `vrika-admin` connect to the **same MongoDB database** (`cipherstrike`). They share:
- `users` collection (authentication)
- `organizations` collection
- `licenses` collection
- `license_customers` collection
- `license_activity` collection

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

- JWT authentication (shared secret with main backend)
- Only `license_admin` or `tenant_admin` roles can access
- Private signing key never leaves this server
- ECDSA P-256 signatures for license integrity
