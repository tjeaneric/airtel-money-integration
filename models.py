from uuid import UUID, uuid4
from database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, Float, String


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sender_phone = Column(String)
    receiver_phone = Column(String)
    amount = Column(Float)
    success = Column(Boolean, default=False)
