from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class Recognition(Base):
    __tablename__ = "recognition"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    date: Mapped[str]
    badge_type: Mapped[str]
    nominator_id: Mapped[int]
