from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ForceReply
from utils.query_utils import get_budget, get_categories, get_category
from utils.crud_utils import insert_budget
from .shared_handlers  import delete_command
from telegram.ext import ConversationHandler, ContextTypes


ACAO_ORC, CATEGORIA_ORC, ASK_VALUE = range(6,9)


async def ask_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        categories_names,e = get_categories()
        if categories_names!= None:
            keybord_options = [[(f"{category_name[0]}")] for category_name in categories_names]
            await update.message.reply_text("Qual o orçamento?", 
                                            reply_markup=ReplyKeyboardMarkup(keybord_options, one_time_keyboard=True,
                                                                                input_field_placeholder="Categoria:"))
            return CATEGORIA_ORC
        if e:
          return await update.message.reply_text(f"Erro ao consultar o banco {e}")
        return await update.message.reply_text("Nenhuma categoria encontrada!")
            

async def options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Abre um selecionador de opções e retorna a opção selecionada!"""
    keyboard_options = [["1"],["2"],["3"]]
    if update.message:
        await update.message.reply_text("Selecione uma opção:\n"\
                                        "1 - Inserir novo orçamento \n" \
                                        "2 - Atualizar orçamento existent\n " \
                                        "3 - Deletar orçamento",
                                                reply_markup=ReplyKeyboardMarkup(keyboard_options, 
                                                one_time_keyboard=True, input_field_placeholder="Selecione uma ação:"))
    return ACAO_ORC
    

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Captura o id da categoria associada ao orçamento a ser editado, inserido ou excluído
    actions ={'1':ask_budget_value,'2':ask_budget_value,'3':delete_command}
    if update.message and update.effective_user and context.user_data:
        category_name = update.message.text
        category, e  = get_category(category_name)
        action = context.user_data.get('action')
        if category:
            budget, e = get_budget(category['id'], update.effective_user.id)
            if budget:
                if action in ['1','2']:
                    context.user_data['budget_id'] = budget.get('id')
                    context.user_data['category_name'] = category.get('name')
                else:
                    context.user_data['delete_model'] = budget
                    context.user_data['delete_id'] = budget.get('id')
        return await actions[str(action)](update, context)


async def handle_options(update : Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and context.user_data:
        option = update.message.text
        if option: 
            context.user_data['action'] = option
            return await ask_category_name(update, context)
            
        



async def ask_budget_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message:
        await update.effective_message.reply_text("Digite um valor para o orçamento", reply_markup=ForceReply())
    return ASK_VALUE


async def handle_budget_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and context.user_data and update.effective_user:
        try:
            if update.message.text:
                budget_value = float(update.message.text.replace(',','.'))
                category_name = context.user_data['category_name']
                user_id = update.effective_user.id
                user_name = update.effective_user.first_name
                action = context.user_data['action']
                if action in ['1', '2']:
                    result, e = insert_budget(budget_value, category_name, user_id)
                    if not e and result:
                        return await update.message.reply_text(f"Orçamento no valor de: R${result.get('value')}\
                                                                em {category_name} salvo!")
                    return await update.message.reply_text(f"Erro ao registrar orçamento {e}")
                return await delete_command(update, context)
        except Exception as e:
           await update.message.reply_text(f"Digite um valor numérico válido ex: 100.00\n {e}")
           return ASK_VALUE
    return ConversationHandler.END
            