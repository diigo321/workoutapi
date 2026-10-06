from uuid import UUID, uuid4
from sqlalchemy import Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class BaseModel(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4, nullable=False)
