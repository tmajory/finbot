import os
import logging
from telegram import Update
from dotenv import load_dotenv
from datetime import datetime as dt
from ai.gemini_client import FinanceAnalyst
from telegram.ext import filters, ContextTypes
from utils.insert_utils import insert_expense, insert_budget, insert_category
from utils.query_utils import get_expenses_by_category, get_monthly_summary

load_dotenv("config/.env")

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

#env variables
TOKEN = os.getenv("TELEGRAM_TOKEN")
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
async def process_message(update) -> dict:
    """recebe a mensagem enviada pelo o usuário e chama o assistente para gerar a resposta
    TODO implementar tratamento de exceção caso gemini falhe, extrair as informações direto do texto."""
    #TODO considerar uso do gemini async para não segurar event loop
    response = assistant.analise(update.message.text)
    return response 


async def process_photo(update):
    photo_file = await update.message.photo[-1].get_file()
    #download temporário da foto
    img_path = await photo_file.download_to_drive(f"temp/{update.message.photo[-1].file_id}.jpg")
    response = assistant.image_analise(img_path)    
    return response     



async def process_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metodo geral, recebe a mensagem testa se foto ou texto e chama a função correta de processamento."""
    type_process = {'photo':process_photo, 'text': process_message}
    response = {}
    if update.message and update.effective_user:
        logger.info(f"Mensagem de {update.effective_user.id}:{update.message.text}")
        for key, func in type_process.items():
            if getattr(update.message, key, None):
                response = await func(update)
                break
        if response:
            value = response.get('Valor', 0)
            category = response.get('Categoria', 'desconhecida')
            description = response.get('Descrição','')
            expense_data = insert_expense(value, category,
                            str(update.effective_user.id), str(update.effective_user.name), description)
            if expense_data:
                if expense_data.get('error'):
                    await update.message.reply_text("Erro ao registrar gasto!")
                    return expense_data.get('error')
                await update.message.reply_text(
                    f"Gasto de R$ {expense_data['data'].get('value'):.2f}\n"
                    f"categoria: {expense_data['data'].get('category')}\n" 
                    f"descrição: {expense_data['data'].get('description')}\n"
                    "Registrado com sucesso!"
                )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando start, mensagem amigável e perguntando qual o registro!"""
    if update.message:
        await update.message.reply_text(
            "Olá! Eu sou o finbot seu assistente financeiro!\n"
            "Como usar:\n"
            "Envie seus gastos: 'Gastei R$ 50 com mercado'\n"
            "Envie comprovante como foto\n"
            "Comandos: /resumo, /categorias, /orcamento, /ajuda"
        )
    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if update.message:
        await update.message.reply_text(
            "*Comandos disponíveis*:\n\n"
            "/start - Iniciar o bot\n"
            "/resumo - ver resumo do mês\n"
            "/categorias - ver gastos por categoria\n"
            "/orcamento - Definir orçamento mensal \n"
            "/ajuda - Mostrar esta mensagem"
        )


async def monthly_summary(update, user_id):
    await update.message.reply_text("Digite o mês do ano em número. Ex: 1(Janeiro)")
    month = int(update.message.text)
    monthly_summary = get_monthly_summary(user_id, month)
    month_name = months_names.get(str(month))
    if monthly_summary != None:
        await update.message.reply_text (f"Resumo do mês de {month_name}\n" 
                                         + f"{key}={value}" for key, value in monthly_summary[0].items())
    await update.message.reply_text(f"Não foi possível gerar o resumo do mês de {month_name}")    

async def category_summary(update, user_id):
    await update.message.reply_text("Qual categoria você gostaria de consultar?")
    category_name = update.message.text
    category_summary = get_expenses_by_category(user_id, category_name)
    if category_summary:
        await update.message.reply_text(f"Total gasto com {category_name} este mês: R$ {category_summary[0].get(category_name):.2f}")
    await update.message.reply_text(f"Não foi encontrado gastos em {category_name} este mês.")


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando que retorna mensagem com o resumo de gastos do mês po categoria
    Futuramente mostrará também estatísticas de orçamento e/ou metas"""
    resume_type = {'1':category_summary ,'2':monthly_summary}
    if update.message:
        await update.message.reply_text("Selecione o resumo: 1: Por categoria(mês atual) \n 2: Mensal")
        for key, func in resume_type.items():
           if update.effective_user: await func(update, str(update.effective_user.id))
           break
        
        


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Método que permite realizar ações no objeto de categorias"""
    commands ={'1': insert_category,'2':insert_category,'3':delete_category}
    if update.message:
        await update.message.reply_text(
            "Selecione uma opção:\n"
            "1 - Adiconar nova categoria\n"
            "2 - Editar Categoria\n"
            "3 - Excluir Categoria\n"
        )


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metodo para definir, editar e deletar orçamentos e metas."""
    commands ={'1': insert_budget,  '2':insert_budget, '3':delete_budget  }
    if update.message:
        await update.message.reply_text(
            "Escolha uma opção:\n"
            "1 - Definir orçamento\n"
            "2 - Editar orçamento\n"
            "3 - Excluir orçamento\n"
        )