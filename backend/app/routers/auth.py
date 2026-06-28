"""Auth router — login and /me for Vrika Admin."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db import get_database
from app.dependencies.auth import require_auth_user
from app.schemas.auth import LoginIn, MeOut, TokenOut
from app.services.jwt_tokens import create_access_token
from app.services.password import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db: AsyncIOMotorDatabase = Depends(get_database)) -> TokenOut:
    email_norm = body.email.lower().strip()
    user = await db.users.find_one({"email": email_norm})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    oid = user["_id"]
    org_id = user["organization_id"]
    roles = user.get("roles") or ["tenant_member"]

    # Only allow license_admin or tenant_admin
    if "license_admin" not in roles and "tenant_admin" not in roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin access required")

    token = create_access_token(
        user_id=str(oid),
        email=user["email"],
        tenant_id=str(org_id),
        roles=roles,
    )
    return TokenOut(access_token=token)


@router.get("/me", response_model=MeOut)
async def me(
    user: dict = Depends(require_auth_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> MeOut:
    org = await db.organizations.find_one({"_id": user["organization_id"]})
    org_name = org.get("name") if org else ""
    return MeOut(
        id=str(user["_id"]),
        email=user["email"],
        username=user.get("username") or "",
        tenant_id=str(user["organization_id"]),
        roles=user.get("roles") or [],
        organization_name=org_name or "",
    )
