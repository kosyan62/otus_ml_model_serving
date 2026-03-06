from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry


class PredictRequest(BaseModel):
    Pregnancies: int = Field(ge=0)
    Glucose: int = Field(ge=0)
    BMI: float = Field(ge=0.0, le=100.0)
    Age: int = Field(ge=0, le=120)


class PredictResponse(BaseModel):
    prediction: int = Field(ge=0, le=1)
