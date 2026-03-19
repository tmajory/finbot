from utils.query_utils import get_categories
from utils.crud_utils import insert_category
from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ForceReply, ReplyKeyboardMarkup


OPCAO, ASK_NAME, DELETE = range(3,6)


async def handle_category_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opts ={'1': ask_category_name,'2':ask_category_name,'3':ask_category_delete}
    if update.message:
        option = update.message.text
        if option not in opts:
            return await update.message.reply_text("Opção inválida! Digite 1, 2 ou 3 ")
        return await opts[option](update,context)



async def handle_category_name(update : Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        category_name = update.message.text
        category, e = insert_category(category_name)
        if e:
            return await update.message.reply_text(f"Erro ao inserir categoria {category_name}: {e}")
        if category:
            return await update.message.reply_text(f"Categoria {category.get('name')} inserida!")
    return ConversationHandler.END
    


async def categories_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Método que permite realizar ações no objeto de categorias"""
    reply_keyboard = [["1"],["2"],["3"]]
    if update.message:
        await update.message.reply_text(
            "Selecione uma opção:\n"
            "1 - Adicionar nova categoria\n"
            "2 - Editar Categoria\n"
            "3 - Excluir Categoria\n", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, 
                                                                        input_field_placeholder="Opção:")
        )
    return OPCAO

      
        
async def ask_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Dê um nome a nova categoria:", reply_markup=ForceReply())
    return ASK_NAME



async def ask_category_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories, e = get_categories()
    if update.message:
        if e:
            await update.message.reply_text(f"Erro ao consultar o banco de dados: {e}")
            return ConversationHandler.END
        if categories:
            await update.message.reply_text("Qual categoria você gostaria de deletar? \n \
                                        TODOS OS GASTOS DESTA CATEGORIA SERÃO APAGADOS",
                                        reply_markup=ReplyKeyboardMarkup(categories,
                                                                            one_time_keyboard=True, input_field_placeholder="Categorias"))
            return DELETE
        await update.message.reply_text("Nenhuma categoria encontrada")



# async def category_delete_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.message:
#         category = update.message.text
#         await update.message.reply_text(f"Certeza que quer deletar a categoria {category}?")
#         return DELETE