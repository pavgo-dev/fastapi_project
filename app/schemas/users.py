from pydantic import BaseModel, Field, field_validator


class CreateUserRequest(BaseModel):
    login: str = Field(max_length=127)

    @field_validator("login")
    @classmethod
    def check_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("login can not be empty")
        if v.lower() in ["admin", "root"]:
            raise ValueError("Name is reserved")

        return v


class CreateUserResponse(CreateUserRequest):
    model_config = {"from_attributes": True}

    id: int
