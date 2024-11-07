from core import SyncCore
from core_orm import SyncORM, AsyncORM
import asyncio
import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
"""Для веб-інтерфейсу"""

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

@app.get("/workers")
async def get_workers():
    workers = SyncORM.data_worker_with_resumes_to_pydantic_model()
    return workers

@app.get("/resume")
async def get_resume():
    workers = SyncORM.select_resumes_with_all_relationships()
    return workers

#SyncORM.create_table_orm()
#SyncCore.insert_workers_core()
#SyncCore.update_workers_core(1, "Lena")
#SyncCore.select_workers_core()
#SyncORM.insert_data_orm()
#SyncORM.update_worker(1, "Misha")
#SyncORM.select_worker_orm()
#SyncORM.create_table_orm()
#asyncio.run(SyncORM.async_insert_resume_model())
#SyncORM.select_resumes_avg_compensation()
#asyncio.run(SyncORM.join_cte_subquery_func())
#SyncORM.select_workers_with_lazy_relationship()
#SyncORM.select_workers_with_join_relationship()
#SyncORM.select_workers_with_selectinload_relationship()
#SyncORM.select_workers_with_condition_relationship()
#SyncORM.select_workers_with_content_eager_relationship()
#SyncORM.select_workers_with_relationship_contains_eagle_with_limit()
#SyncORM.data_worker_to_pydantic_model()
#SyncORM.data_worker_with_resumes_to_pydantic_model()
#SyncORM.add_vacancies_and_replies()
SyncORM.select_resumes_with_all_relationships()