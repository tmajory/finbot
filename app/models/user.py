from base import BaseModel
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped,mapped_column, relationship
from sqlalchemy import String

#User entity declaration

if TYPE_CHECKING:#Circular importation prevent
    from expense import Expense
    from budget import Budget

class User(BaseModel):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'finbot'}

    nickname : Mapped[str] = mapped_column(String(50), unique=True)#Unique nickname
    #Expenses table relationship configuration
    expenses : Mapped[List["Expense"]] = relationship(
        back_populates = "user",
        lazy="selectin")
    #Budgets table relationship configuration
    budgets : Mapped[List["Budget"]] = relationship(
        back_populates="user",
        lazy="selectin")
