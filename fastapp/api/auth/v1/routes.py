from fastapi import APIRouter, Depends, status, Response, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

import config
from fastapp import dependencies, models, schemas, crud, exceptions
from fastapp.database import get_db
from fastapp.tasks import celery_tasks


router = APIRouter(prefix="/v1", tags=["v1"])

oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/send_code", status_code=status.HTTP_200_OK)
async def send_code(email_schema: schemas.Email, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    email: str = email_schema.email
    try:
        code = await crud.create_code(db, email)
    except exceptions.CodeMoreThanExisting:
        raise exceptions.AuthFailedException(detail="Code has already sent. Try later")

    message_title = f"Verifying on {config.PROJECT_TITLE}"
    message_body = f"Activation Code:\n{code}"

    celery_tasks.send_mail.delay(email, message_title, message_body)

    return JSONResponse({"status": "success"})



@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.JwtTokenGet)
async def register(response: Response, user_schema: schemas.UserCreate, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    user: models.User | None = await crud.get_user_by_email(db, user_schema.email)

    if user:
        raise exceptions.AuthFailedException(detail="Email is already registered")
     
    code: models.Code | None = await crud.get_code_by_user_email_and_code(db, user_schema.email, user_schema.code)

    if not code:
        raise exceptions.AuthFailedException(detail="Incorrect code")
    
    user: models.User = await crud.create_user(db, user_schema)

    celery_tasks.delete_codes_by_email.delay(user.email)

    token_pair: schemas.TokenPair = dependencies.create_token_pair(user_id=user.id)
    dependencies.add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return token_pair.access



@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.JwtTokenGet)
async def login(response: Response, user_login: schemas.UserLogin, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    user: models.User = await crud.get_user_by_email(db, user_login.email)

    if not user:
        raise exceptions.NotFoundException("Account isn't registered. Please register first.")
    
    code: models.User | None = await crud.get_code_by_user_email_and_code(db, user_login.email, user_login.code)

    if not code:
        raise exceptions.AuthFailedException("Incorrect code")

    celery_tasks.delete_codes_by_email.delay(user.email)

    token_pair: schemas.TokenPair  = dependencies.create_token_pair(user_id=user.id)
    dependencies.add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return token_pair.access


@router.post("/refresh_token", response_model=schemas.JwtTokenGet)
async def refresh_token(refresh_token: str | None = Cookie()):
    if not refresh_token:
        raise exceptions.BadRequestException(detail="refresh token required")

    jwt_token: schemas.JwtTokenGet = dependencies.refresh_token_state(token=refresh_token)

    return jwt_token


@router.post("/logout")
async def logout(response: Response, ) -> JSONResponse:
    dependencies.remove_refresh_token_from_cookie(response)
