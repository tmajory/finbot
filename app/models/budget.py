from datetime import datetime, date
from .base import BaseModel
from typing import Optional, TYPE_CHECKING
from sqlalchemy.sql import functions as func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy import Numeric, Date, ForeignKey, UniqueConstraint, select, extract


if TYPE_CHECKING:
    from user import User
    from category import Category

#Budget class

class Budget(BaseModel):

    __tablename__ ='budget'
    __table_args__ = (UniqueConstraint('category_id', 'date', name='uq_budget_category_date'),)

 
    value: Mapped[float] = mapped_column(Numeric(10,2), nullable=False)#Value of the expense
    date: Mapped[Date] = mapped_column(Date, default = date.today)#Date of the expense
    
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))#Foreign key of users table
    category_id : Mapped[int] = mapped_column(ForeignKey('category.id'))#Foreign key of the categories table

    user: Mapped[Optional["User"]] = relationship(back_populates="budgets")
    category: Mapped[Optional["Category"]] = relationship(back_populates="budgets")

    
    def save_budget(self, session: Session, **kwargs):
        #Atualiza orçamento validando se o valor foi enviado.
        value = kwargs.get("value")
        if value == None or value <= 0:
            return "Orçamento não pode ser definido com valor nulo"
        return self.save(session,**kwargs )


    @classmethod
    def budget_by_category(cls, session: Session, user_id: int, category_id: int):
        """Return the budget of the month and category specified"""
        stmt = select(cls).where(cls.user_id==user_id).\
            where(cls.category_id==category_id)
        budget = session.scalar(stmt)
        return budget
    
    @classmethod
    def budget_total_by_category(cls, session: Session, user_id:int, category_id: int, year: int):
        """Return the total value of a budget of a specified category"""
        stmt = select(func.sum(cls.value)).where(cls.user_id==user_id).\
            where(cls.category_id==category_id).where(extract('year',cls.date)==year)
        budget_value = session.scalar(stmt)
        return budget_value

    @classmethod
    def budget_by_category_month_year(cls, session: Session, user_id: int, category_id: int, month = None , year = None):
        """Pesquisa no banco budget por categoria mês e ano
        Usa caso não passado mês e ano atuais."""
        now = datetime.now().date()
        month = month or now.month
        year = year or now.year
        try:
            stmt = select(cls).where(Budget.user_id==user_id).\
            where(Budget.category_id==category_id).where(extract('month',Budget.date)==month).\
            where(extract('year',Budget.date)==year)
            budget = session.scalar(stmt)
            return budget, None
        except Exception as e:
            return None, e