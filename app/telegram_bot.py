import os
import logging
from telegram import Update
from database import create_db
from dotenv import load_dotenv
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ConversationHandler)
from bot.bot_commands import (start, help_command, process_data, resume_command, escolha, handle_escolha, handle_month,
                              category_summary, category_handle, cancelar_command, categories_command, budget_command, 
                              ESCOLHA, MES, CATEGORIA)


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

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("ajuda",help_command))
    app.add_handler(CommandHandler("categorias",categories_command))
    app.add_handler(CommandHandler("orcamento", budget_command))    
    app.add_handler(resume_handler)
    app.add_handler(MessageHandler(filters.PHOTO | filters.TEXT  & ~filters.COMMAND, process_data))
    
    

    #Iniciar bot
    print("Bot iniciado! Pressione ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__=='__main__':
    main()
