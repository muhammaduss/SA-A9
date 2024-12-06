from pydantic import BaseModel


class ReceiveMessage(BaseModel):
    user_alias: str
    message: str
