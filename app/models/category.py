from .base import BaseModel
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String


if TYPE_CHECKING:
    from expense import Expense
    from budget import Budget

#Category entity declaration

class Category(BaseModel):
    __tablename__ = 'category'


    name : Mapped[str] = mapped_column(String(50), unique=True)#Unique name 
    #Expenses table relationship configuration
    expenses : Mapped[List["Expense"]] = relationship(
        back_populates="category",
        lazy="selectin")
    #Budgets table relationship configuration
    budgets : Mapped[List["Budget"]] = relationship(
        back_populates="category",
        lazy="selectin")

    