#Metódos de inserção de dados para uso no bot_commands
import logging
from models.expense import Expense
from models.category import Category
from models.budget import Budget
from models.user import User
from database.session_manager import get_session

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

def insert_category(category_name):
    """Verify if exists in database, create if not and return the instance"""
    with get_session() as session:
        try:
            category, e = Category().get_by_name(session, category_name)
            if not isinstance(category, Category):
                category, e = Category().save(session, name = category_name)
            if category:
                return category.to_dict(), e
        except Exception as e:
            logger.error(f"Erro ao inserir categoria: {e}", exc_info=True)
            return None, e
        return None, None

def insert_user(user_id, user_name, user_nickname):
    """Verify if exists in database, create if not and return the instance"""
    with get_session() as session:
        try:
            user, e = User().get_by_id(session, user_id)
            if not user:            
                user, e  = User().save(session, telegram_id = user_id, name = user_name, nick_name = user_nickname)
        except Exception as e: 
            logger.error(f"Erro ao inserir categoria: {e}", exc_info=True)
            return None, e
        return user, e

def insert_expense(value:float, category_name:str, user_id:str, user_name: str, description:str):
    """Testa se existem user e category passados e insere expense no banco"""
    with get_session() as session:
        try: 
            user, e = User().get_by_id(session, user_id)
            category, e = insert_category(category_name)
            if isinstance(user, User) and isinstance(category, Category):
                expense, e  = Expense().save(session, user_id = user_id, category_id = category.id, 
                                            value = value, description = description)
                if isinstance(expense, Expense):
                    return expense.to_dict(), None
            return None, None
        except Exception as e:
            logger.error(f"Erro ao inserir categoria: {e}", exc_info=True)
            return None, e
        

def insert_budget(value:float, category_name, user_id):
    """Testa se existem user e category passados e insere budget no banco"""
    with get_session() as session:
        try:
            user, e = User().get_by_id(session, user_id)
            category, e = insert_category(category_name)
            if isinstance(user, User) and isinstance(category, Category):
                budget, e = Budget().save_budget(session, user_id = user_id, category_id= category.id, value = value)
                if isinstance(budget, Budget):
                   return budget.to_dict(), None
            return None, None
        except Exception as e:
            logger.error(f"Erro ao inserir categoria: {e}", exc_info=True)
            return None, e

def delete_instance(model_class, instance_id):    
    with get_session() as session:
        try:
            instance, e = model_class.get_by_id(session, instance_id)
            model_class.delete(instance, session)
            return instance.to_dict(), None
        except Exception as e:
            logger.error(f"Erro ao inserir categoria: {e}", exc_info=True)
            return None, e
    
        
