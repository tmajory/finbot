import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class FinanceAnalyst:

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def analise(self, message):
        prompt = f""" Extraia as informações deste gasto: "{message}"
        Responda APENAS com JSON no formato:
        {{"valor":0.00,"categoria":"string","descricao":"string"}}
        """

        response = self.model.generate_content(prompt)
        return response.text