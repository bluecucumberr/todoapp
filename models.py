# Тут описывается структура базы данных: какие есть таблицы (User, Task) и как они связаны.
# models.py — база данных
#

from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass

# tg_id — Telegram ID, по нему идёт привязка пользователей.
# id — автоинкрементный ID в таблице.
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)

# Это задачи пользователя. Каждая связана с user (внешний ключ ForeignKey).
# completed — булево значение (выполнена или нет).
# title — текст задачи.
class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    completed: Mapped[bool] = mapped_column(default=False)
    user: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

# При старте API создаёт таблицы, если их ещё нет.
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
