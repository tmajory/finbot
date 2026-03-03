import google.generativeai as genai
import PIL.Image
import json


class FinanceAnalyst:

    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        

    def analise(self, message) -> dict:
        prompt = f""" Extraia as informações deste gasto: "{message}"
        Responda APENAS com JSON no formato:
        {{"Valor":0.00,"Categoria":"String","Descricao":"string"}}
        Categoria deve ser generalizada e sempre iniciar com a letra maiúscula, exemplo se gasto em farmácia ou hospital então categoria é Saúde
        """

        response = self.model.generate_content(prompt)
        return json.loads(response.text)

    def image_analise(self, image_path) -> dict:
        img = PIL.Image.open(image_path)

        prompt = f"""Extraia as informações deste comprovante/recibo,
        Retorne apenas no formato:
        {{"Valor":0.00, "Categoria":"string", "Descricao":"string"}}
        """

        response = self.model.generate_content([prompt,img])
        return json.loads(response.text)