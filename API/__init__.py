from pydantic import BaseModel


class BaseResponse(BaseModel):
    code: int
    payload: dict
