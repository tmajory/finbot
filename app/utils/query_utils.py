#Métodos de acesso aos dados do banco para serem usados no comando resumo e no dashboard
from datetime import datetime, date
from models.expense import Expense
from models.category import Category
from database.session_manager import get_session
from sqlalchemy import select, extract,func
from typing import List


def get_monthly_summary(user_id, month):
    data = {}
    with get_session() as session:
        try:
            categories, e = Category.get_all(session)
            if not categories: return data, e
            for category in categories:
                value = Expense.expenses_total(session, user_id, category.id, month)
                data.update({str(category.name):value })
            return data, None
        except Exception as e:
            return None, e


def get_expenses_by_category(user_id, category_name):
    data = {}
    atual_date = datetime.now().date()
    with get_session() as session:
        try: 
            category, e = Category.get_by_name(session, category_name)
            if isinstance(category, Category):
                stmt = select(extract('month', Expense.date),func.sum(Expense.value)).where(Expense.user_id==user_id).where(Expense.category_id==category.id).\
                where(extract('year', Expense.date)==atual_date.year).\
                where(extract('month', Expense.date)<=atual_date.month).\
                group_by(extract('month', Expense.date)).\
                order_by(extract('month', Expense.date))
                expenses = session.execute(stmt).all()
                data = {str(int(month)): value for month, value in expenses}
                return data, None
            return data, None
        except Exception as e:
            return data, e



def get_categories():
    categories_names = []
    with get_session() as session:
        try:
            categories, e = Category.get_all(session)
            if categories:
                categories_names = [[categorie.name] for categorie in categories]
            return categories_names, None
        except Exception as e:
            return None, e