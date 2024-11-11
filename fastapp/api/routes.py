from fastapi import APIRouter

from .v1.routes import router as v1_router
from .auth.v1.routes import router as v1_auth_router

router = APIRouter()

router.include_router(v1_router)
router.include_router(v1_auth_router, prefix="/auth")