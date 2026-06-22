import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    login: str = Field(max_length=127)


class CreateUserRequest(UserBase):
    @field_validator("login")
    @classmethod
    def check_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("login can not be empty")
        if v.lower() in ["admin", "root"]:
            raise ValueError("Name is reserved")

        return v


class CreateUserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
