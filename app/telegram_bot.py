#type: ignore
import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bot.bot_commands import resume_command, categories_command, budget_command
from ai.gemini_client import FinanceAnalyst
from dotenv import load_dotenv
from telegram import Update


load_dotenv("config/.env")

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assistant = FinanceAnalyst(GEMINI_API_KEY)

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando start, mensagem amigável e perguntando qual o registro!"""
    await update.message.reply_text(
        "Olá! Eu sou o finbot seu assistente financeiro!\n"
        "Como usar:\n"
        "Envie seus gastos: 'Gastei R$ 50 com mercado'\n"
        "Envie comprovante como foto\n"
        "Comandos: /resumo, /categorias, /orcamento, /ajuda"
    )
    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Comandos disponíveis*:\n\n"
        "/start - Iniciar o bot\n"
        "/resumo - ver resumo do mês\n"
        "/categorias - ver gastos por categoria\n"
        "/orcamento - Definir orçamento mensal \n"
        "/ajuda - Mostrar esta mensagem"
    )


async def process_message(message:str) -> dict:
    """recebe a mensagem enviada pelo o usuário e chama o assistente para gerar a resposta
    TODO implementar tratamento de exceção caso gemini falhe, extrair as informações direto do texto."""
    response = assistant.analise(message)
    return response 



async def process_photo(image_path):
    response = assistant.image_analise(image_path)
    return response     


async def process_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metodo geral, recebe a mensagem testa se foto ou texto e chama a função correta de processamento."""
    logger.info(f"Mensagem de {update.effective_user.id}:{update.message.text}")#type: ignore
    response = {}
    await update.message.reply_text("Processando seu registro...")
    if update.message.text:
       user_message = update.message.text
       response = process_message(user_message)
    elif update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        #download temporário da foto
        img_path = await photo_file.download_to_drive(f"temp/{update.message.photo[-1].file_id}.jpg")
        response = process_photo(img_path)
    await update.message.reply_text(
        f"Gasto de R$ {response.get('valor',0):.2f}," 
        f"categoria: {response.get('categoria','desconhecida')}," 
        f"descrição: {response.get('descricao','')}\n"
        "Registrado com sucesso!"
    )


def main():
    """Inicializa o bot"""

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
