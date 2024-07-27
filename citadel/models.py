from sqlmodel import Field, SQLModel


class Test(SQLModel, table=True):
    """The created tests."""

    id: int | None = Field(default=None, primary_key=True)
    name: str


class Question(SQLModel, table=True):
    """The questions associated with tests."""

    id: int | None = Field(default=None, primary_key=True)
    question: str
    answer: str
    test_id: int = Field(foreign_key="test.id")
