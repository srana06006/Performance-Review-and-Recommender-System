from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    date: Mapped[str]
    type: Mapped[str]
    severity: Mapped[str]
