from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from models import WorkloadModel

class WorkersAddDTO(BaseModel):
    """Для post запитів"""
    username: str

class WorkersDTO(BaseModel):
    """Для get запитів"""
    id: int
    username: str

class ResumeAddDTO(BaseModel):
    title: str
    compensation: Optional[int]
    workload: WorkloadModel
    worker_id: int

class ResumeDTO(BaseModel):
    id: int
    title: str
    compensation: Optional[int]
    workload: WorkloadModel
    worker_id: int
    created_at: datetime
    updated_at: datetime

class ResumesRelDTO(ResumeDTO):
    worker: list["WorkersDTO"]

class WorkersRelDTO(WorkersDTO):
    resumes: list["ResumeDTO"]

class VacanciesAddDTO(BaseModel):
    title: str
    compensation: Optional[int]

class VacanciesDTO(BaseModel):
    id: int


class ResumesRelVacanciesRepliedWithoutVacancyCompensationDTO(ResumeDTO):
    worker: "WorkersDTO"
    vacancies_replied: list["VacanciesWithoutCompensationDTO"]


class VacanciesWithoutCompensationDTO(BaseModel):
    id: int
    title: str