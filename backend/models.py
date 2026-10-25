"""Explicit request/response models; server-owned fields cannot be submitted."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-z0-9_]+$")
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def normalise_username(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class AccountPublic(BaseModel):
    id: int
    username: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class ProfileWrite(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    display_name: str = Field(min_length=1, max_length=100)
    contact_info: str | None = Field(default=None, max_length=200)
    city: Literal["HK", "SH"]
    preferred_role: Literal["Frontend", "Backend", "Database", "Agentic Development", "Other"]
    languages: list[Literal["Mandarin", "Cantonese", "English"]] = Field(max_length=3)

    @field_validator("display_name", "contact_info", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("languages")
    @classmethod
    def distinct_languages(cls, value):
        return list(dict.fromkeys(value))


class ProfilePublic(ProfileWrite):
    account_id: int
    in_team: int
    updated_at: str
