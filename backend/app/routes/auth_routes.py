from fastapi import APIRouter
from app.schemas.user_schema import SignupRequest, LoginRequest, AuthResponse
from app.services.auth_service import signup_user, login_user

router = APIRouter()


@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest):
    result = await signup_user(request.name, request.email, request.password)
    return AuthResponse(**result)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    result = await login_user(request.email, request.password)
    return AuthResponse(**result)