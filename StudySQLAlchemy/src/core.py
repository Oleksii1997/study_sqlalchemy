import asyncio
from models import metadata_obj_imperative, workers_core

from connect_database import sync_engine, async_engine
from sqlalchemy import text, insert, select, update


class SyncCore:
    """Клас роботи з БД в імперативному стилі"""

    @staticmethod
    def create_tables():
        """Створюємо синхронно таблиці"""
        # metadata_obj.drop_all(sync_engine) #щоб перед запуском функції всі попередні таблиці видалялися(якщо це потрібно)
        metadata_obj_imperative.create_all(sync_engine)

    @staticmethod
    def insert_workers_core():
        """Приклад запиту на додавання даних до таблиці з використвнням функціоналу SQLAlchemy (QueryBuilder)"""
        with sync_engine.connect() as conn:
            stmt = insert(workers_core).values(
                [
                    {'username': 'Alisa'},
                    {'username': 'Alex'}
                ]
            )
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def select_workers_core():
        sync_engine.echo = True
        with sync_engine.connect() as conn:
            query = select(workers_core) #SELECT * FROM workersCore
            result = conn.execute(query)
            print(result.all())

    @staticmethod
    def update_workers_core_sql(user_id: int, new_username: str):
        """Приклад оновлення імені користувача, з використанням SQL запиту, потрібно звернути увагу на синтаксис
        підстановки даних в запит, тут f-рядки не можна використовувати
        bindparams - захист від sql - ін'єкцій!!!"""

        sync_engine.echo = True
        with sync_engine.connect() as conn:
            stmt = text("UPDATE workers_core SET username=:new_username WHERE id=:user_id")
            stmt = stmt.bindparams(new_username=new_username, user_id=user_id)
            conn.execute(stmt)
            conn.commit()

    @staticmethod
    def update_workers_core(user_id: int, new_username: str):
        """Приклад оновлення імені користувача, з використанням функцій SQLAlechemy"""
        sync_engine.echo = True
        with sync_engine.connect() as conn:
            stmt = (
                update(workers_core)
                .values(username=new_username)
                #.where(workers_core.c.id == user_id)
                .filter_by(id=user_id)
            )
            conn.execute(stmt)
            conn.commit()

"""Файл роботи з таблицею за допомогою запитів SQL без використання ORM SQLAlchemy"""
"""Приклад синхронного та асинхронного запиту"""
"""
with sync_engine.connect() as conn:
    res = conn.execute(text("SELECT VERSION()"))
    print(f"{res.all()}")

async def async_work():
    async with async_engine.connect() as my_conn:
        my_res = await my_conn.execute(text("SELECT 1,2,3 union select 4,5,6"))
        print(f"{my_res.all()}")


asyncio.run(async_work())
"""

"""Приклад запиту на додавання даних до таблиці з використвнням чистого sql запиту"""
"""
def insert_data_sql():
    with sync_engine.connect() as conn:
        stmt = "INSERT INTO workers (username) VALUES ('Bobr'), ('Volk');"
        conn.execute(text(stmt))
        conn.commit()
"""