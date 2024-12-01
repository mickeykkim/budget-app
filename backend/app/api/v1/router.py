from fastapi import APIRouter

from app.api.v1.endpoints import auth, bank_accounts, transactions
from app.api.v1.endpoints.oauth import router as oauth_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    bank_accounts.router, prefix="/bank-accounts", tags=["bank-accounts"]
)
api_router.include_router(
    transactions.router, prefix="/transactions", tags=["transactions"]
)
api_router.include_router(oauth_router, prefix="/oauth", tags=["oauth"])
