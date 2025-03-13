from pydantic import BaseModel, validator
from typing import Optional

class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str

    @validator("password")
    def check_credentials(cls, v, values):
        if not any(
                [values.get('username'),
                 values.get('email'),
                 values.get('phone')]
        ):
            raise ValueError(
                "At least one of "
                "'username', "
                "'email', or "
                "'phone' must be provided"
            )
        return v