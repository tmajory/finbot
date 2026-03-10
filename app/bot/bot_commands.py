#TODO Implementar budget_command e category_commands, usando conversation handler
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv
from datetime import datetime as dt
from ai.gemini_client import FinanceAnalyst
from telegram.ext import filters, ContextTypes, ConversationHandler, MessageHandler
from utils.insert_utils import insert_expense, insert_budget, insert_category
from utils.query_utils import get_expenses_by_category, get_monthly_summary, get_categories

load_dotenv("config/.env")

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

#env variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assistant = FinanceAnalyst(GEMINI_API_KEY)

ESCOLHA, CATEGORIA, MES = range(3)

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


async def monthly_summary(update, context: ContextTypes.DEFAULT_TYPE):
    """Pergunta sobre o mês que deve ser retornado o resumo"""
    reply_keyboard = [[m] for m in months_names.keys()]
    await update.message.reply_text("Digite o mês do ano em número. Ex: 1(Janeiro)",
                                    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                                                       input_field_placeholder="mês?"))
    return MES


async def category_summary(update, context: ContextTypes.DEFAULT_TYPE):
    """Pergunta a categoria que o usuário gostaria de ver e retorna"""
    reply_keyboard = get_categories()[0]
    if not reply_keyboard:
        await update.message.reply_text("Não foram encontradas categorias no banco de dados!")
        return ConversationHandler.END
    await update.message.reply_text("Qual categoria você gostaria de consultar?",
                                   reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True,
                                    input_field_placeholder="Categoria"))
    return CATEGORIA

async def escolha(update, context: ContextTypes.DEFAULT_TYPE):
    """Retorna a escolha do tipo de resumo se de categoria ou de um mês específico"""
    reply_keyboard =[['1'],['2']]
    await update.message.reply_text("Qual o tipo de resumo você gostaria de consultar? \n" \
    "1 - Resumo de gastos em uma categoria de janeiro até o mês atual\n" \
    "2 - Resumo de gastos no mês atual por categora.\n", reply_markup = ReplyKeyboardMarkup(reply_keyboard,
                                                        one_time_keyboard=True, input_field_placeholder="Tipo resumo:"))
    return ESCOLHA


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await escolha(update, context)
    return ESCOLHA


async def handle_escolha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = {'1':category_summary, '2':monthly_summary}
    if update.message:
        option = update.message.text   
        if option in options:
            return await options[option](update,context)
        await update.message.reply_text("Opção inválida! Digite 1 ou 2")
        return ESCOLHA

async def handle_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.effective_user:
        month = update.message.text
        user_id = str(update.effective_user.id)
        if month not in months_names: 
            await update.message.reply_text("Mês não encontrado") 
            return ConversationHandler.END
        data, e = get_monthly_summary(user_id, int(month)) 
        if  e or not data:
            await update.message.reply_text("Não foi possível gerar o resumo")
            return ConversationHandler.END
        lines = "\n".join(f"{months_names.get(k,k)}: R$ {v:.2f}" for k,v in data.items())
        await update.message.reply_text(f"Resumo do mês de {months_names.get(month)}\n\n {lines}",
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END


async def category_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.effective_user:
        category = update.message.text
        user_id = update.effective_user.id
        data, e = get_expenses_by_category(user_id, category)
        if e or not data:
            await update.message.reply_text(f"Não foi possível gerar resumo para categoria {category}")
            return ConversationHandler.END
        lines = "\n".join(f"{months_names.get(k,k)}: R$ {v:.2f}" for k,v in data.items())
        await update.message.reply_text(f"Resumo de gastos em {category} até {months_names.get(str(atual_month))}\n\n {lines}",
                                        reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

async def cancelar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Cancelando operação")
        return ConversationHandler.END



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