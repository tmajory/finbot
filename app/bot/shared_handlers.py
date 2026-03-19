import os
import logging
from dotenv import load_dotenv
from ai.gemini_client import FinanceAnalyst
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, ContextTypes
from utils.crud_utils import delete_instance, insert_expense


load_dotenv("config/.env")

#logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
assistant = FinanceAnalyst(GEMINI_API_KEY)


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

async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data:
        if update.message:
            model_class = context.user_data.get('delete_model')
            instance_id = context.user_data.get('delete_id')
            if not model_class or not instance_id:
                await update.message.reply_text("Nenhum item selecionado para deletar")
                return ConversationHandler.END
            result, e = delete_instance(model_class, instance_id)
            if result:
                await update.message.reply_text(f"{result.get('name')} deletado com sucesso!", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(f"Erro ao deletar! {e}")
            return ConversationHandler.END
 

async def cancelar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Cancelando operação")
        return ConversationHandler.END

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
            expense_data, e = insert_expense(value, category,
                            str(update.effective_user.id), str(update.effective_user.name), description)
            if e or expense_data == None:
                await update.message.reply_text("Erro ao registrar gasto!")
                return e
            await update.message.reply_text(
                f"Gasto de R$ {expense_data.get('value'):.2f}\n"
                f"categoria: {expense_data.get('category')}\n" 
                f"descrição: {expense_data.get('description')}\n"
                "Registrado com sucesso!"
            )
