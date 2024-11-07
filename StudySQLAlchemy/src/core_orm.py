from sqlalchemy import text, insert, select, cast, Numeric, Integer, and_, func
from connect_database import sync_engine, async_engine, session_factory, async_session_factory
from models import metadata_obj_declarative, WorkersORM, ResumeModel, Vacancies, VacanciesReplies
from sqlalchemy.orm import aliased, joinedload, selectinload, contains_eager
from refact_pydantic import (ResumeDTO, ResumeAddDTO, ResumesRelDTO, WorkersDTO, WorkersAddDTO, WorkersRelDTO,
                             WorkloadModel,
                             VacanciesDTO, VacanciesAddDTO, ResumesRelVacanciesRepliedWithoutVacancyCompensationDTO)
class SyncORM:
    """Класс створення та роботи з таблицею за допомогою ORM синхронно"""

    @staticmethod
    def create_table_orm():
        sync_engine.echo = True
        metadata_obj_declarative.create_all(sync_engine)

    @staticmethod
    def delete_table():
        sync_engine.echo = True
        metadata_obj_declarative.drop_all(bind=sync_engine, tables=[WorkersORM.__table__])

    @staticmethod
    def insert_data_orm():
        with session_factory() as session:
            some_worker_sem = WorkersORM(username="Bob")
            some_worker_alex = WorkersORM(username="Alex")
            some_worker_bob = WorkersORM(username="Oleksander")
            # session.add(some_worker_sem)
            session.add_all([some_worker_sem, some_worker_bob, some_worker_alex])
            session.flush() #відправляє зміни які є в сесії в БД але при цьому сесію не завершає
            session.commit()

    @staticmethod
    async def async_insert_resume_model():
        async with async_session_factory() as session:
            resume_1 = ResumeModel(title="Python developer", workload="parttime", compensation=13000, worker_id=1)
            resume_2 = ResumeModel(title="Python Data Engineer", workload="fulltime", compensation=4000, worker_id=2)
            resume_3 = ResumeModel(title="Python backend developer", workload="parttime", compensation=7500, worker_id=3)
            resume_4 = ResumeModel(title="Python data science", workload="fulltime", compensation=20000, worker_id=1)
            # session.add(some_worker_sem)
            session.add_all([resume_1, resume_2, resume_3, resume_4])
            await session.commit()

    @staticmethod
    def select_resumes_avg_compensation(like_language: str = "Python"):
        """
        select workload, avg(compensation)::int as avg_compensation
        from resume
        where title like '%Python%' and compensation > 3000
        group by workload
        """
        with session_factory() as session:
            query = (
                select(
                    ResumeModel.workload,
                    cast(func.avg(ResumeModel.compensation), Integer).label("avg_compensation"),
                )
                .select_from(ResumeModel)
                .filter(and_(
                    ResumeModel.title.contains(like_language),
                    ResumeModel.compensation > 3000,
                ))
                .group_by(ResumeModel.workload)
                .having(cast(func.avg(ResumeModel.compensation), Integer) > 3000)
            )
            print(query.compile(compile_kwargs={"literal_binds": True}))
            res = session.execute(query)
            result = res.all()
            print(result)

    @staticmethod
    async def join_cte_subquery_func(like_lenguage: str = "Python"):
        """WITH helper2 as (
            SELECT *, compensation-avg_workload_compensation as diff_compensation
            FROM
            (SELECT
                w.id,
                w.username,
                r.compensation,
                r.workload,
                avg(r.compensation) OVER (PARTITION BY workload)::int AS avg_workload_compensation
            FROM resume r
            JOIN "workersORM" w ON r.worker_id = w.id) helper1
        )
        SELECT * FROM helper2
        ORDER BY diff_compensation DESC"""
        async with async_session_factory() as session:
            r = aliased(ResumeModel)
            w = aliased(WorkersORM)
            subq = (
                select(
                    r,
                    w,
                    func.avg(r.compensation).over(partition_by=r.workload).cast(Integer).label("avg_workload_compensation")
                )
                .select_from(r)
                .join(w, r.worker_id == w.id).subquery("helper1")
            )
            cte = (
                select(
                    subq.c.worker_id,
                    subq.c.username,
                    subq.c.compensation,
                    subq.c.workload,
                    subq.c.avg_workload_compensation,
                    (subq.c.compensation - subq.c.avg_workload_compensation).label("diff_compensation")
                )
                .cte("helper2")
            )
            query = (
                select(cte)
                .order_by(cte.c.diff_compensation.desc())
            )
            #print(query.compile(compile_kwargs={"literal_binds": True}))
            res = await session.execute(query)
            result = res.all()
            print(f"{result}=")


    @staticmethod
    def select_worker_orm():
        """Запит до моделі працівників, щоб отримати вс"""
        with session_factory() as session:
            #worker_id = 2
            #worker_orm = session.get(WorkersORM, worker_id)
            query = select(WorkersORM)
            result = session.execute(query)
            workers = result.scalars().all()
            print(f"{workers}")
            for worker in workers:
                print(f"Працівник {worker.id} - {worker.username}")

    @staticmethod
    def update_worker(worker_id: int, new_username: str):
        """Приклад оновлення даних в таблиці працівників"""
        with session_factory() as session:
            worker = session.get(WorkersORM, worker_id)
            worker.username = new_username
            #session.refresh(worker) #оновлює дані про об'єкт з бази даних якщо в нього хтось вніс зміни
            # session.expire(worker) """Скидає всі зміни по об'єкту worker які були зроблені до цього часу"""
            # session.expire_all() """Скидає всі зміни по всіх об'єктах які були зроблені і ніякий запит в базу не відправляється,
            # це синхронна операція"""
            session.commit()

    @staticmethod
    def select_workers_with_lazy_relationship():
        """При такому способі у нас в базу відправляється N+1 запит (1 щоб дістати всіх воркерів і далі
        по одному запиту на кожне резюме)
        !!!!! В асинхронній версії алхімії ми не можемо використовувати ліниву підгрузку"""
        with session_factory() as session:
            query = (
                select(WorkersORM)
            )
            res = session.execute(query)
            result = res.scalars().all()
            worker_1 = result[0].resumes
            print(worker_1)
            worker_2 = result[1].resumes
            print(worker_2)

    @staticmethod
    def select_workers_with_join_relationship():
        """Таким способом ми одразу забираєме усі дані, запит відправляється в базу один.
        В даному випадку в одного робітника може бути багато резюме, тобто маємо випадок
        One-To-Many, а joinedload для такого варіанту не підходить.
        joinedload підходить до Many-to-One або One-to-One завантаження"""

        with session_factory() as session:
            query = (
                select(WorkersORM)
                .options(joinedload(WorkersORM.resumes))
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            worker_1 = result[0].resumes
            print(worker_1)
            worker_2 = result[1].resumes
            print(worker_2)

    @staticmethod
    def select_workers_with_selectinload_relationship():
        """selectionload підходить до One-to-Many або Many-to-Many завантаження"""

        with session_factory() as session:
            query = (
                select(WorkersORM)
                .options(selectinload(WorkersORM.resumes))
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            worker_1 = result[0].resumes
            print(worker_1)
            worker_2 = result[1].resumes
            print(worker_2)

    @staticmethod
    def select_workers_with_condition_relationship():
        with session_factory() as session:
            query = (
                select(WorkersORM)
                .options(selectinload(WorkersORM.resumes_parttime))
            )
            res = session.execute(query)
            result = res.scalars().all()

            print(result)

    @staticmethod
    def select_workers_with_content_eager_relationship():
        """Для того щоб була вкладена структура а не таблична"""
        with session_factory() as session:
            query = (
                select(WorkersORM)
                .join(ResumeModel, ResumeModel.worker_id == WorkersORM.id)
                .options(contains_eager(WorkersORM.resumes))
                .filter(ResumeModel.workload == "parttime")
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            print("++++++")
            print(result)

    @staticmethod
    def select_workers_with_relationship_contains_eagle_with_limit():
        """З лімітом результатів які потрібно повернути, в одного коритувача повертаємо 1 резюме"""
        with session_factory() as session:
            subq = (
                select(ResumeModel.id.label("parttime_resume_id"))
                .filter(ResumeModel.worker_id == WorkersORM.id)
                .order_by(WorkersORM.id.desc())
                .limit(1)
                .scalar_subquery()
                .correlate(WorkersORM)
            )
            query = (
                select(WorkersORM)
                .join(ResumeModel, ResumeModel.id.in_(subq))
                .options(contains_eager(WorkersORM.resumes))
            )
            res = session.execute(query)
            result = res.unique().scalars().all()
            for some_result in result:
                print("++++++")
                print(some_result.resumes)

    @staticmethod
    def data_worker_to_pydantic_model():
        """Перетворення даних алхімії в pydantic модель"""
        with session_factory() as session:
            query = (
                select(WorkersORM)
                .limit(2)
            )
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"Result ORM = {result_orm}")
            result_dto = [WorkersDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"Result DTO = {result_dto}")

    @staticmethod
    def data_worker_with_resumes_to_pydantic_model():
        """Перетворення даних алхімії в pydantic модель"""
        with session_factory() as session:
            query = (
                select(WorkersORM)
                .options(selectinload(WorkersORM.resumes))
                .limit(2)
            )
            res = session.execute(query)
            result_orm = res.scalars().all()
            print(f"Result ORM = {result_orm}")
            result_dto = [WorkersRelDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"Result DTO = {result_dto}")
            return result_dto

    @staticmethod
    def select_resumes_with_all_relationships():
        with session_factory() as session:
            query = (
                select(ResumeModel)
                .options(joinedload(ResumeModel.worker))
                .options(selectinload(ResumeModel.vacancies_replied).load_only(Vacancies.title))
            )
            res = session.execute(query)
            result_orm = res.unique().scalars().all()
            print(f"Result ORM = {result_orm}")
            result_dto = [ResumesRelVacanciesRepliedWithoutVacancyCompensationDTO.model_validate(row, from_attributes=True) for row in result_orm]
            print(f"Result DTO = {result_dto}")
            return result_dto

    @staticmethod
    def add_vacancies_and_replies():
        with session_factory() as session:
            new_vacancy = Vacancies(title="Python розробник", compensation=100000)
            resume_1 = session.get(ResumeModel, 1)
            resume_2 = session.get(ResumeModel, 2)
            resume_1.vacancies_replied.append(new_vacancy)
            resume_2.vacancies_replied.append(new_vacancy)
            session.commit()

class AsyncORM:
    """Класс створення та роботи з таблицею за допомогою ORM асинхронно"""
    @staticmethod
    async def async_insert_data_orm():
        async with async_session_factory() as session:
            some_worker_sem = WorkersORM(username="Anna")
            some_worker_alex = WorkersORM(username="Marta")
            some_worker_bob = WorkersORM(username="Lena")
            # session.add(some_worker_sem)
            session.add_all([some_worker_sem, some_worker_bob, some_worker_alex])
            await session.commit()

