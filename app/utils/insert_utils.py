#Metódos de inserção de dados para uso no bot_commands
from models.expense import Expense
from models.category import Category
from models.budget import Budget
from models.user import User
from database.session_manager import get_session



def insert_category(session, category_name):
    """Verify if exists in database, create if not and return the instance"""
    category, e = Category().get_by_name(session, category_name)
    if not category:
        category, e = Category().save(session, name = category_name)
    return category,e

def insert_user(session, user_id, user_name):
    """Verify if exists in database, create if not and return the instance"""
    user, e = User().get_by_id(session, user_id)
    if not user:            
        user, e  = User().save(session,id = user_id, name = user_name)
    return user, e

def insert_expense(value:float, category_name:str, user_id:str, user_name: str , description:str):
    """Testa se existem user e category passados e insere expense no banco"""
    with get_session() as session:
        try: 
            user, e = insert_user(session, user_id, user_name)
            category, e = insert_category(session, category_name)
            if isinstance(user, User) and isinstance(category, Category):
                expense, e  = Expense().save(session, user_id = user_id, category_id = category.id, 
                                            value = value, description = description)
                if isinstance(expense, Expense):
                    return {'Success': True, 'data':expense.to_dict() ,'Message':'Gasto salvo com sucesso!'}
        except Exception as e:
            return {'Sucess':False, 'error':str(e)}
        

def insert_budget(value:float, category_name, user_id, user_name):
    """Testa se existem user e category passados e insere budget no banco"""
    with get_session() as session:
        try:
            user, e = insert_user(session, user_id, user_name)
            category, e = insert_category(session, category_name)
            if isinstance(user, User) and isinstance(category, Category):
                budget, e = Budget().save_budget(session, user_id = user_id, category_id= category.id, value = value)
                if isinstance(budget, Budget):
                    return {'Success':True, 'data':budget.to_dict(),'Message':'Orçamento salvo com sucesso!'}
        except Exception as e:
            return{'Success':False, "error":str(e)}
   