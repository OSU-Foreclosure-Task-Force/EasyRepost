from sqlmodel import SQLModel, Field


class Hub(SQLModel, table=True):
    name: str = Field(index=True, primary_key=True)
    url: str = Field(default=None)
