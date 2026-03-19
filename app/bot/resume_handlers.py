from datetime import datetime as dt
from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from utils.query_utils import get_categories, get_expenses_by_category, get_monthly_summary


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