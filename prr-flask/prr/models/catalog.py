from sqlalchemy.orm import Mapped, mapped_column
from prr.models.base import Base
class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[str]
    title: Mapped[str]
    provider: Mapped[str]
    modality: Mapped[str]
    duration_h: Mapped[int]
    skills_json: Mapped[str]
    price: Mapped[int]
    internal_flag: Mapped[bool]
