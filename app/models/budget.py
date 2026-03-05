from user import User
from typing import Optional
from datetime import date
from base import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, Date, ForeignKey


#Budget class

class Budget(BaseModel):

    __tablename__ ='budget'
    __table_args__ = {'schema':'finbot'}

    value: Mapped[float] = mapped_column(Numeric(10,2))#Value of the expense
    date: Mapped[Date] = mapped_column(Date, default = date.today)#Date of the expense
    
    user_id: Mapped[int] = mapped_column(ForeignKey('finbot.user.id'))#Foreign key of users table
    category_id : Mapped[int] = mapped_column(ForeignKey('finbot.category.id'))#Foreign key of the categories table

    users: Mapped[Optional["User"]] = relationship("budgets")



