import datetime
import enum
from typing import Annotated, Optional

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, text, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship, contains_eager
from sqlalchemy.orm import DeclarativeBase

"""
    alembic init src/migrations - команда для створення директорії та налаштувань міграцій
    alembic revision --autogenerate - команда для створення міграцій
"""

"""
    Annotated - для створення певного типу об'єкту який характеризує 
    поле в базі даних та його повторного використвнння
"""
str_256 = Annotated[str, 256]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('UTC', now())"))]
class Base(DeclarativeBase):
    """клас який будемо використовувати для створення наших моделей"""
    type_annotation_map = {
        str_256: String(256)
    }
    repr_cols_num = 3 #кількість колонок які виводяться при виводі можелі
    repr_cols = tuple()# сюди можна дописати назву колонки яку потрібно вивести додатково

    def __repr__(self):
        """Функція яка задає вигляд того як ми виводимо нашу модель в консоль.
        Relationships не використовується в repr(), так як може призводити до непередбачуваних
        додаткових запитів в БД та підвантаження даних"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {','.join(cols)}>"

metadata_obj_declarative = Base().metadata
class WorkersORM(Base):
    """Створення моделі працівників в деклеративному стилі"""
    __tablename__ = "workersORM"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()

    resumes: Mapped[list["ResumeModel"]] = relationship(
        back_populates="worker"
    )

    resumes_parttime: Mapped[list["ResumeModel"]] = relationship(
        back_populates="worker",
        primaryjoin="and_(WorkersORM.id == ResumeModel.worker_id, ResumeModel.workload == 'parttime')",
        order_by="ResumeModel.id.desc()",
    )
class WorkloadModel(enum.Enum):
    """Клас для поля вибору значень 'зі списку'"""
    parttime = "parttime"
    fulltime = "fulltime"

class ResumeModel(Base):
    """Модель резюме"""
    __tablename__ = "resume"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    workload: Mapped[WorkloadModel]
    compensation: Mapped[int] = mapped_column()
    worker_id: Mapped[int] = mapped_column(ForeignKey("workersORM.id", ondelete="CASCADE"))
    created_at: Mapped[created_at]
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('UTC', now())"),
                                                          onupdate=datetime.datetime.now(datetime.UTC))

    worker: Mapped["WorkersORM"] = relationship(
        back_populates="resumes"
    )

    vacancies_replied: Mapped[list["Vacancies"]] = relationship(
        back_populates="resumes_replied",
        secondary="vacancies_replies"
    )
    __table_args__ = (
        Index("title_index", "title"),
        CheckConstraint("compensation > 0", name="checl_compensation_positive")
    )

class Vacancies(Base):
    """Модель вакансій"""
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str_256]
    compensation: Mapped[Optional[int]]

    resumes_replied: Mapped[list["ResumeModel"]] = relationship(
        back_populates="vacancies_replied",
        secondary="vacancies_replies"
    )

class VacanciesReplies(Base):
    """Модель відгуків на вакансію, для зв'язків мені-ту-мені !!!!!"""
    __tablename__ = "vacancies_replies"

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resume.id", ondelete="CASCADE"),
        primary_key=True
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        primary_key=True
    )
    cover_letter: Mapped[Optional[str]]


"""Створюємо модель таблиці в імперативному стилі"""
metadata_obj_imperative = MetaData()
workers_core = Table(
    "workers_core",
    metadata_obj_imperative,
    Column("id", Integer, primary_key=True),
    Column("username", String)
)
