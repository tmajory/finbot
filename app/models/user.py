from .base import BaseModel
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped,mapped_column, relationship,synonym
from sqlalchemy import String, select

#User entity declaration

if TYPE_CHECKING:#Circular importation prevent
    from expense import Expense
    from budget import Budget

class User(BaseModel):
    __tablename__ = 'user'

    telegram_id : Mapped[str] = mapped_column('telegram_id', String(100), unique=True)
    name : Mapped[str] = mapped_column('nickname', String(50))#nickname


    #Expenses table relationship configuration
    expenses : Mapped[List["Expense"]] = relationship(
        back_populates = "user",
        lazy="selectin")
    #Budgets table relationship configuration
    budgets : Mapped[List["Budget"]] = relationship(
        back_populates="user",
        lazy="selectin")

    @classmethod
    def get_by_id(cls, session, id):
        try:
            stmt = select(cls).where(User.telegram_id==id)
            user = session.scalar(stmt)
            if isinstance(user, User):
                return user, None
            return None, None
        except Exception as e:
            return None, e
        