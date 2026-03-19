#TODO Implementar budget_command e category_commands, usando conversation handler
import os
import logging
from telegram import Update
from dotenv import load_dotenv
from datetime import datetime as dt
from utils.crud_utils import insert_user
from ai.gemini_client import FinanceAnalyst
from .resume_handlers import escolha, ESCOLHA
from .budget_handlers import options, ACAO_ORC
from .category_handlers import categories_options, OPCAO
from telegram.ext import filters, ContextTypes, ConversationHandler, MessageHandler

load_dotenv("config/.env")

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

#env variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assistant = FinanceAnalyst(GEMINI_API_KEY)




#Global variables
atual_month =  dt.date(dt.now()).month

months_names ={
    '1':'Janeiro',
    '2':'Fevereiro',
    '3':'Março',
    '4':'Abril',
    '5':'Maio',
    '6':'Junho',
    '7':'Julho',
    '8':'Agosto',
    '9':'Setembro',
    '10':'Outubro',
    '11':'Novembro',
    '12':'Dezembro',
}


#Methods



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando start, mensagem amigável e perguntando qual o registro!"""
    if update.message and update.effective_user:
        user, e = insert_user(update.effective_user.id, update.effective_user.first_name, update.effective_user.name)
        if user:
            logger.info(f"Usuário: {user.name} de id:{user.id} salvo com sucesso!")
        if e:
            logger.error(f"Erro ao salvar usuário: {e}", exc_info=True)
        await update.message.reply_text(
            "Olá! Eu sou o finbot seu assistente financeiro!\n"
            "Como usar:\n"
            "Envie seus gastos: 'Gastei R$ 50 com mercado'\n"
            "Envie comprovante como foto\n"
            "Comandos: /resumo, /categorias, /orcamento, /ajuda, /cancelar"
        )
    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if update.message:
        await update.message.reply_text(
            "*Comandos disponíveis*:\n\n"
            "/start - Iniciar o bot\n"
            "/resumo - ver resumo do mês atual ou por categoria até o mês atual.\n"
            "/categorias - ver gastos por categoria\n"
            "/orcamento - Definir orçamento mensal \n"
            "/ajuda - Mostrar esta mensagem"
        )


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await escolha(update, context)
    return ESCOLHA


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metodo para definir, editar e deletar orçamentos e metas."""
    await options(update, context)
    return ACAO_ORC

  

async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await categories_options(update, context)
    return OPCAO