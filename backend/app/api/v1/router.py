# app/api/v1/router.py

from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, aws, bank_accounts, oauth, transactions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    bank_accounts.router, prefix="/bank-accounts", tags=["bank-accounts"]
)
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
api_router.include_router(aws.router, prefix="/aws", tags=["aws"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["oauth"])
