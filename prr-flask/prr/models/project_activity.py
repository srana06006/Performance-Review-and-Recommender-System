from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class ProjectActivity(Base):
    __tablename__ = "project_activity"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int]
    date: Mapped[str]
    project_id: Mapped[str]
    role: Mapped[str]
    hours: Mapped[float]
    velocity: Mapped[int]
    quality_score: Mapped[float]
    on_time: Mapped[bool]
    customer_impact: Mapped[int]
