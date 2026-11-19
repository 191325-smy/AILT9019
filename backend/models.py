"""Explicit request/response models; server-owned fields cannot be submitted."""

from typing import Literal

from pydantic import (BaseModel, ConfigDict, Field, SecretStr, field_validator,
                      model_validator)


Role = Literal["Frontend", "Backend", "Database", "Agentic Development", "Other"]
Programme = Literal[
    "AI and Data Science",
    "Applied AI",
    "Computer Science",
    "Others",
]
SkillFlag = Literal[0, 1]


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
    preferred_role: Role
    languages: list[Literal["Mandarin", "Cantonese", "English"]] = Field(max_length=3)
    programme: Programme | None = None
    open_roles: list[Role] | None = Field(default=None, max_length=5)
    programming: SkillFlag | None = None
    github: SkillFlag | None = None
    debugging: SkillFlag | None = None
    web: SkillFlag | None = None
    ai_agent: SkillFlag | None = None

    @field_validator("display_name", "contact_info", mode="before")
    @classmethod
    def trim_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("languages")
    @classmethod
    def distinct_languages(cls, value):
        return list(dict.fromkeys(value))

    @field_validator("open_roles")
    @classmethod
    def distinct_roles(cls, value):
        if value is None:
            return value
        return list(dict.fromkeys(value))

    @model_validator(mode="after")
    def roles_include_preferred(self):
        if self.open_roles and self.preferred_role not in self.open_roles:
            raise ValueError("open_roles must include preferred_role")
        return self


class ProfilePublic(ProfileWrite):
    account_id: int
    in_team: int
    updated_at: str
