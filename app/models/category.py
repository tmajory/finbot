from base import BaseModel
from typing import List
from expense import Expense
from budget import Budget
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer

#Category entity declaration

class Category(BaseModel):
    __tablename__ = 'category'
    __table_args__ = {'schema': 'finbot'}

    name : Mapped[str] = mapped_column(String(50), unique=True)#Unique name 
    #Expenses table relationship configuration
    expenses : Mapped[List["Expense"]] = relationship(
        back_populates="expenses",
        lazy="selectin")
    #Budgets table relationship configuration
    budgets : Mapped[List["Budget"]] = relationship(
        back_populates="budgets",
        lazy="selectin")
