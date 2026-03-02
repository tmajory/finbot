from telegram import Update
from telegram.ext import filters, ContextTypes
from datetime import datetime as dt

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

async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando que retorna mensagem com o resumo de gastos do mês po categoria
    Futuramente mostrará também estatísticas de orçamento e/ou metas"""
    await update.message.reply_text(
        f"Resumo do mês de {months_names.get(str(atual_month))}:\n\n"
        #TODO: Laço que percorre as categorias existentes no sistema e retorna os gastos com cada uma
        #TODO: view no banco que atualize sempre que esse comando for chamado e retorne os dados 
        "Alimentação: R$ 50,00\n"
        "Saúde: R$ 100,00\n"
    )


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Método que permite realizar ações no objeto de categorias"""
    await update.message.reply_text(
        "Selecione uma opção:\n"
        "1 - Adiconar nova categoria\n"
        "2 - Editar Categoria\n"
        "3 - Excluir Categoria\n"
    )


async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Metodo para definir, editar e deletar orçamentos e metas."""
    await update.message.reply_text(
        "Escolha uma opção:\n"
        "1 - Definir orçamento\n"
        "2 - Editar orçamento\n"
        "3 - Excluir orçamento\n"
    )