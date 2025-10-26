from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class ManagerReview(Base):
    __tablename__ = "manager_review"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    period: Mapped[str]
    dimension: Mapped[str]
    rating: Mapped[int]
    narrative_redacted: Mapped[str]
