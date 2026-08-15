from pydantic import BaseModel


class MessageResponse(BaseModel):
    message: str


class IDResponse(BaseModel):
    message: str
    id: str