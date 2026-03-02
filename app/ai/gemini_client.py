import google.generativeai as genai
import json


class FinanceAnalyst:

    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def analise(self, message):
        prompt = f""" Extraia as informações deste gasto: "{message}"
        Responda APENAS com JSON no formato:
        {{"valor":0.00,"categoria":"string","descricao":"string"}}
        Categoria deve ser generalizada e sempre iniciar com a letra maiúscula, exemplo se gasto em farmácia ou hospital então categoria é Saúde
        """

        response = self.model.generate_content(prompt)
        return json.loads(response.text)