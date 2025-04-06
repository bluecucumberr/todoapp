# Это не про HTTP-запросы — это слой работы с базой (можно назвать db.py), 
# где пишутся функции, которые читают/пишут данные.
# requests.py — бизнес-логика


from sqlalchemy import select, update, delete, func
from models import async_session, User, Task
from pydantic import BaseModel, ConfigDict
from typing import List


class TaskSchema(BaseModel):
    id: int
    title: str
    completed: bool
    user: int

    model_config = ConfigDict(from_attributes=True)

# Если пользователь уже есть — возвращает его.
# Если нет — создаёт нового.
async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user
        
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
# Возвращает все невыполненные задачи для пользователя.
async def get_tasks(user_id):
    async with async_session() as session:
        tasks = await session.scalars(
            select(Task).where(Task.user == user_id, Task.completed == False)
        )

        serialized_tasks = [
            TaskSchema.model_validate(t).model_dump() for t in tasks
        ]

        return serialized_tasks
    
# Возвращает кол-во выполненных задач.
async def get_completed_tasks_count(user_id):
    async with async_session() as session:
        return await session.scalar(select(func(Task.id)).where(Task.completed == True))