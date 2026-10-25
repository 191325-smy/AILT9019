"""FastAPI app: account lifecycle and authenticated writes to one's own profile."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .models import AccountPublic, Credentials, LoginResponse, ProfilePublic, ProfileWrite
from .security import hash_password, new_token, verify_password
from .store import DuplicateUsername, Store


DEFAULT_DB = Path(__file__).resolve().parents[1] / "matching" / "ailt9019.db"
bearer = HTTPBearer(auto_error=False)


def unauthorised():
    return HTTPException(status_code=401, detail="Invalid or expired login credentials.",
                         headers={"WWW-Authenticate": "Bearer"})


def create_app(db_path: Path | str | None = None, session_ttl_seconds: int | None = None,
               allowed_origins: list[str] | None = None) -> FastAPI:
    path = Path(db_path if db_path is not None else os.getenv("DB_PATH", str(DEFAULT_DB))).expanduser().resolve()
    ttl = session_ttl_seconds if session_ttl_seconds is not None else int(os.getenv("SESSION_TTL_SECONDS", "3600"))
    if not isinstance(ttl, int) or isinstance(ttl, bool) or not 1 <= ttl <= 604800:
        raise ValueError("SESSION_TTL_SECONDS must be an integer from 1 to 604800.")
    origins = allowed_origins if allowed_origins is not None else [
        origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
    if "*" in origins:
        raise ValueError("Configure explicit ALLOWED_ORIGINS rather than '*'.")
    store = Store(path)

    @asynccontextmanager
    async def lifespan(application):
        store.initialise()
        yield

    application = FastAPI(title="AILT9019 Accounts and Profiles", version="1.0.0", lifespan=lifespan)
    application.state.store = store
    application.add_middleware(CORSMiddleware, allow_origins=origins,
                               allow_methods=["GET", "POST", "PUT"],
                               allow_headers=["Authorization", "Content-Type"], allow_credentials=False)

    @application.middleware("http")
    async def private_responses(request: Request, call_next):
        response = await call_next(request)
        if request.url.path.startswith(("/auth/", "/profiles/")):
            response.headers["Cache-Control"] = "no-store"
        return response

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        # FastAPI's default validation response includes submitted values.
        # Keep actionable field errors without echoing passwords or contacts.
        detail = [{"loc": error["loc"], "msg": error["msg"], "type": error["type"]} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": detail})

    def current_account(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if credentials is None or not 20 <= len(credentials.credentials) <= 200:
            raise unauthorised()
        account = store.session_account(credentials.credentials)
        if account is None:
            raise unauthorised()
        return account

    @application.get("/health")
    def health():
        return {"status": "ok"}

    @application.post("/auth/register", response_model=AccountPublic, status_code=201)
    def register(credentials: Credentials):
        try:
            return store.create_account(credentials.username, hash_password(credentials.password.get_secret_value()))
        except DuplicateUsername:
            raise HTTPException(status_code=409, detail="Username is already registered.") from None

    @application.post("/auth/login", response_model=LoginResponse)
    def login(credentials: Credentials):
        account = store.account_for_login(credentials.username)
        valid = verify_password(credentials.password.get_secret_value(), account["password_hash"] if account else None)
        if not valid:
            raise unauthorised()
        token = new_token()
        store.create_session(account["id"], token, ttl)
        return {"access_token": token, "token_type": "bearer", "expires_in": ttl}

    @application.get("/auth/me", response_model=AccountPublic)
    def who_am_i(account=Depends(current_account)):
        return account

    @application.post("/auth/logout", status_code=204)
    def logout(account=Depends(current_account), credentials=Depends(bearer)):
        store.revoke_session(credentials.credentials)
        return Response(status_code=204)

    @application.get("/profiles/me", response_model=ProfilePublic)
    def get_profile(account=Depends(current_account)):
        profile = store.load_profile(account["id"])
        if profile is None:
            raise HTTPException(status_code=404, detail="Profile not created yet; save it with PUT /profiles/me.")
        return profile

    @application.put("/profiles/me", response_model=ProfilePublic)
    def save_profile(values: ProfileWrite, account=Depends(current_account)):
        return store.save_profile(account["id"], values.model_dump())

    return application


app = create_app()
