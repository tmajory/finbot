import os
import logging
from telegram import Update
from database import create_db
from dotenv import load_dotenv
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, 
                          ConversationHandler,CallbackQueryHandler)
from bot.bot_commands import (start, help_command, resume_command, budget_command, 
                              categories_command)
from bot.budget_handlers import CATEGORIA_ORC, ASK_VALUE, ACAO_ORC, handle_budget, handle_budget_value, handle_options
from bot.resume_handlers import ESCOLHA, MES, CATEGORIA, handle_escolha, handle_month, category_handle
from bot.category_handlers import OPCAO, ASK_NAME, DELETE, handle_category_name, handle_category_options
from bot.shared_handlers import process_data, cancelar_command, delete_command



load_dotenv("config/.env")

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    """Inicializa o bot""" 
    create_db()
    if not TOKEN:
        return "Não foi possível localizar o Token de acesso ao bot."
    
    resume_handler = ConversationHandler(
        entry_points=[CommandHandler("resumo", resume_command)],
        states={ESCOLHA : [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_escolha)],
                MES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_month)],
                CATEGORIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_handle)]
            },
            fallbacks=[CommandHandler("cancelar",cancelar_command)]
    )

    budget_handler = ConversationHandler(
        entry_points=[CommandHandler("orcamento", budget_command)],
        states = {
                ACAO_ORC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_options)],
                CATEGORIA_ORC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget)],
                ASK_VALUE : [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget_value)]
            },
        fallbacks=[CommandHandler("cancelar", cancelar_command)]
    )
    
    category_handler = ConversationHandler(
        entry_points= [CommandHandler("categorias", categories_command)],
        states = {
            OPCAO:[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_category_options)],
            ASK_NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND,handle_category_name)],
                #   DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND,category_delete_handle)]
                },
        fallbacks=[CommandHandler("cancelar",cancelar_command)]
    )

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("ajuda",help_command))
    app.add_handler(category_handler)
    app.add_handler(resume_handler)
    app.add_handler(budget_handler)    
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT  & ~filters.COMMAND, process_data))
    
    

    #Iniciar bot
    print("Bot iniciado! Pressione ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__=='__main__':
    main()
