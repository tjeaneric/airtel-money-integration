from typing import List, Union
from pydantic import BaseModel


class transactionBase(BaseModel):
    id: int
    amount: int
    success: bool = False

    class Config:
        orm_mode = True
