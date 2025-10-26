from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class Feedback360(Base):
    __tablename__ = "feedback360"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    rater_id: Mapped[int]
    date: Mapped[str]
    dimension: Mapped[str]
    rating: Mapped[int]
    relationship: Mapped[str]
    comment_redacted: Mapped[str]
