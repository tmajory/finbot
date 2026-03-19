from datetime import datetime as dt
from .base import BaseModel
from typing import Optional, TYPE_CHECKING
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy import Numeric, Date, String, ForeignKey, extract, select


if TYPE_CHECKING:
    from user import User
    from category import Category    

#Expenses class

class Expense(BaseModel):

    __tablename__ ='expense'

    value: Mapped[float] = mapped_column(Numeric(10,2))#Value of the expense
    date: Mapped[Date] = mapped_column(Date, default= lambda: dt.date(dt.now()))#Date of the expense
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))#Foreign key of users table
    description: Mapped[str] = mapped_column(String(150), default='')#Small text description about the expense
    category_id : Mapped[int] = mapped_column(ForeignKey('category.id'))#Foreign key of the categories table
    
    #Relationship declaration
    user: Mapped[Optional["User"]] = relationship(back_populates="expenses")
    category: Mapped[Optional["Category"]] = relationship(back_populates="expenses")


    @classmethod
    def expenses_total(cls, session: Session, user_id:int, category_id = None, month = None):
        """Return the expenses sum or total or filtered by category and month
        """
        stmt =  select(func.sum(cls.value)).where(cls.user_id==user_id)
        if category_id and month:
            stmt = stmt.where(cls.category_id==category_id).where(extract('month',cls.date) == month)
        sum_value = session.scalar(stmt)
        return sum_value
    
    @classmethod
    def expenses_total_by_category(cls, session: Session, category_id:int, user_id:str):
        """Return the total expenses of that category"""
        stmt =  select(func.sum(cls.value)).where(cls.category_id==category_id).where(cls.user_id==user_id)\
            .where(extract('month',cls.date)== dt.date(dt.now()).month)
        sum_by_category = session.scalar(stmt)
        return sum_by_category


    @classmethod
    def expenses_count_by_category(cls, session: Session, category_id):
        """Return the number of expenses with that category id"""
        stmt = select(func.count(cls.id)).where(cls.category_id==category_id)
        count_expenses = session.scalar(stmt)
        return count_expenses