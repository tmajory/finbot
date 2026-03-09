from telegram.ext import Application, CommandHandler, MessageHandler, filters
from bot.bot_commands import *
from telegram import Update


def main():
    """Inicializa o bot"""
    if not TOKEN:
        return "Não foi possível localizar o Token de acesso ao bot."

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("ajuda",help_command))
    app.add_handler(CommandHandler("resumo",resume_command))
    app.add_handler(CommandHandler("categorias",categories_command))
    app.add_handler(CommandHandler("orcamento", budget_command))

    
    
    app.add_handler(MessageHandler(filters.PHOTO | filters.Text  and ~filters.COMMAND, process_data))
    
    

    #Iniciar bot
    print("Bot iniciado! Pressione ctrl+C para parar.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__=='__main__':
    main()
