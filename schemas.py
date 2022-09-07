from uuid import uuid4
from pydantic import BaseModel


class transactionBase(BaseModel):
    sender_phone: str
    receiver_phone: str
    amount: float

    class Config:
        orm_mode = True
