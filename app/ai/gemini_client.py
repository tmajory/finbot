import json
import PIL.Image
from google import genai



class FinanceAnalyst:

    def __init__(self, api_key):
        client = genai.Client(api_key=api_key)
        self.client = client
        
        

    def analise(self, message):
        prompt = f""" Extraia as informações deste gasto: "{message}"
        Responda APENAS com String no formato:
        {{"Valor":'float',"Categoria":"String","Descricao":"String"}}
        Categoria deve ser generalizada e sempre iniciar com a letra maiúscula, exemplo se gasto em farmácia ou hospital então categoria é Saúde
        """

        response = self.client.models.generate_content(model='gemini-2.5-flash',contents=prompt)
        if response.text == None:
            return {
                'Success': False,
                'Message': 'Retorno da genai vazio',
                'data': None
            }
        return json.loads(response.text)

    def image_analise(self, image_path) -> dict:
        img = PIL.Image.open(image_path)

        prompt = f"""Extraia as informações deste comprovante/recibo,
        Retorne apenas no formato:
        {{"Valor":0.00, "Categoria":"string", "Descricao":"string"}}
        """

        response = self.client.models.generate_content(model='gemini-2.5-flash',contents=[prompt,img])
        if response.text == None:
            return {
                'Success': False,
                'Message': 'Retorno da genai vazio',
                'data': None
            }
        return json.loads(response.text)
    


# if __name__ == '__main__':
#     ai = FinanceAnalyst(api_key)
#     # response  = ai.client.models.list()
#     # print(response.page)
#     response = ai.analise('100 reais em lanchonete')
#     print(response)
#     # txt = '```json\n{"Valor":100.0,"Categoria":"Alimentação","Descricao":"Gasto em lanchonete"}\n```'
#     # txt = re.split('json',txt)
#     # print(txt)