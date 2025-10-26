from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class OKR(Base):
    __tablename__ = "okr"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    period: Mapped[str]
    objective: Mapped[str]
    kr: Mapped[str]
    target: Mapped[float]
    achieved: Mapped[float]
    weight: Mapped[float]
