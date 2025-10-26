from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class Employee(Base):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    org_unit: Mapped[str]
    manager_id: Mapped[int | None]
    current_rank: Mapped[str]
    last_promotion_date: Mapped[str]
    location: Mapped[str]
    employment_type: Mapped[str]
