from base import BaseModel
from typing import Optional
from datetime import date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, Date, String, ForeignKey
from user import User

#Expenses class

class Expense(BaseModel):

    __tablename__ ='expense'
    __table_args__ = {'schema':'finbot'}

    value: Mapped[float] = mapped_column(Numeric(10,2))#Value of the expense
    date: Mapped[Date] = mapped_column(Date, default= date.today)#Date of the expense
    user_id: Mapped[int] = mapped_column(ForeignKey('finbot.user.id'))#Foreign key of users table
    description: Mapped[str] = mapped_column(String(150), default='')#Small text description about the expense
    category_id : Mapped[int] = mapped_column(ForeignKey('finbot.category.id'))#Foreign key of the categories table
    
    #Relationship declaration
    user: Mapped[Optional["User"]] = relationship(back_populates="expenses")
