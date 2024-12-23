from typing import Optional
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import select
from database import async_session, engine
from pydantic import BaseModel, Field

Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class BaseResponse(BaseModel):
    success: bool = Field(True)
    message: str = Field("Action completed successfully")


class DataResponse(BaseResponse):
    payload: BaseModel


class DataListResponse(BaseResponse):
    payloads: list[BaseModel]


class BaseWithUtils(Base):
    __abstract__ = True

    @classmethod
    async def get(cls, id: int) -> "BaseWithUtils":
        """Get the record with the specified ID"""
        async with async_session() as session:
            statement = select(cls).where(cls.id == id)
            result = await session.execute(statement)
            instance = result.scalars().first()
            if instance is None:
                raise NoResultFound(f"No record found with ID {id}")
            return instance

    @classmethod
    async def get_multiple(cls, limit: Optional[int] = None) -> list["BaseWithUtils"]:
        """Get a specified number of records, default to all"""
        async with async_session() as session:
            statement = select(cls)
            if limit:
                statement = statement.limit(limit)
            result = await session.execute(statement)
            return list(result.scalars().all())

    @classmethod
    async def create(cls, **kwargs) -> "BaseWithUtils":
        """Create a new record"""
        async with async_session() as session:
            instance = cls(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def update(cls, id: int, **kwargs) -> "BaseWithUtils":
        """Update the record with the specified ID"""
        async with async_session() as session:
            instance = await cls.get(id)
            if not instance:
                raise NoResultFound(f"No record found with ID {id}")

            for key, value in kwargs.items():
                setattr(instance, key, value)

            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    @classmethod
    async def delete(cls, id: int) -> bool:
        """Delete the record with the specified ID"""
        async with async_session() as session:
            instance = await cls.get(id)
            if not instance:
                return False

            await session.delete(instance)
            await session.commit()
            return True

    def to_dict(self, exclude_none: bool = False) -> dict:
        """
        Convert a model instance to a dictionary.
        """
        if exclude_none:
            return {column.name: getattr(self, column.name) for column in self.__table__.columns if getattr(self, column.name) is not None}
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
