"""Create an admin user for the Vrika Admin portal.

Usage:
    python -m app.scripts.create_admin --email admin@example.com --password secret123 --username Admin

    Or inside Docker:
    docker compose exec admin-api python -m app.scripts.create_admin --email admin@example.com --password secret123
"""

import argparse
import asyncio
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings
from app.services.password import hash_password


async def create_admin(email: str, password: str, username: str, org_name: str) -> None:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db]

    email_norm = email.lower().strip()

    # Check if user already exists
    existing = await db.users.find_one({"email": email_norm})
    if existing:
        print(f"❌ User with email '{email_norm}' already exists.")
        roles = existing.get("roles", [])
        if "license_admin" not in roles:
            roles.append("license_admin")
            await db.users.update_one({"_id": existing["_id"]}, {"$set": {"roles": roles}})
            print(f"✅ Added 'license_admin' role to existing user.")
        else:
            print(f"ℹ️  User already has 'license_admin' role.")
        client.close()
        return

    # Create or find organization
    org = await db.organizations.find_one({"name": org_name})
    if not org:
        org_doc = {
            "name": org_name,
            "slug": org_name.lower().replace(" ", "-"),
            "created_at": datetime.now(UTC),
        }
        result = await db.organizations.insert_one(org_doc)
        org_id = result.inserted_id
        print(f"✅ Created organization: {org_name}")
    else:
        org_id = org["_id"]
        print(f"ℹ️  Using existing organization: {org_name}")

    # Create admin user
    user_doc = {
        "email": email_norm,
        "username": username.strip(),
        "password_hash": hash_password(password),
        "organization_id": org_id,
        "roles": ["tenant_admin", "license_admin"],
        "created_at": datetime.now(UTC),
    }
    result = await db.users.insert_one(user_doc)
    print(f"✅ Admin user created!")
    print(f"   Email: {email_norm}")
    print(f"   Username: {username}")
    print(f"   Roles: tenant_admin, license_admin")
    print(f"   User ID: {result.inserted_id}")

    client.close()


def main():
    parser = argparse.ArgumentParser(description="Create an admin user for Vrika Admin portal")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    parser.add_argument("--username", default="Admin", help="Display name (default: Admin)")
    parser.add_argument("--org", default="Vrika", help="Organization name (default: Vrika)")
    args = parser.parse_args()

    asyncio.run(create_admin(args.email, args.password, args.username, args.org))


if __name__ == "__main__":
    main()
