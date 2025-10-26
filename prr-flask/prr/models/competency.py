from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class CompetencyFramework(Base):
    __tablename__ = "competency_framework"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rank: Mapped[str]
    competency: Mapped[str]
    expected_level: Mapped[int]
    rubric_json: Mapped[str]
