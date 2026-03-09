#Métodos de acesso aos dados do banco para serem usados no comando resumo e no dashboard
from models.expense import Expense
from models.category import Category
from database.session_manager import get_session



def get_monthly_summary(user_id, month):
    data = {}
    with get_session() as session:
        try:
            categories, e = Category.get_all(session)
            if categories:
                for category in categories:
                    value = Expense.expenses_total(session, user_id, category.id, month)
                    data.update({str(category.name):value })
                return data, None
        except Exception as e:
            return data, e

def get_expenses_by_category(user_id, category_name):
    data = {}
    with get_session() as session:
        try: 
            category, e = Category.get_by_name(session, category_name)
            if isinstance(category, Category):
                value = Expense.expenses_total_by_category(session, category.id, user_id)
                data.update({category_name:value})
                return data, None
        except Exception as e:
            return data, e