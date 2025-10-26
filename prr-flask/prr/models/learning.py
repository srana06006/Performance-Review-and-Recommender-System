from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class LearningHistory(Base):
    __tablename__ = "learning_history"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    course_id: Mapped[str]
    start_dt: Mapped[str]
    end_dt: Mapped[str]
    completion: Mapped[bool]
    assessment_score: Mapped[int | None]
    hours: Mapped[int]
