import openai
import tenacity
import numpy as np

class OpenAIModel:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        openai.api_key = self.api_key

    @tenacity.retry(wait=tenacity.wait_exponential(multiplier=1, min=4, max=30))
    def completion_with_backoff(self, **kwargs):
        try:
            return openai.ChatCompletion.create(**kwargs)
        except Exception as e:
            print(e)
            raise e   

    def chat(self, system_prompt, user_prompt):
        response = None
        try:
            response = self.completion_with_backoff(
                model=self.engine,
                temperature=0,
                messages= [
                    {"role": "system", "content" : system_prompt},
                    {"role": "user", "content" : user_prompt}
                ]
            )
        except Exception as e:
            print('Error:', e)
            return

        result = ''
        for choice in response.choices:
            result += choice.message['content']
       
        return result
    
    def calculate_similarity(self, input_text1, input_text2):
        try:
            resp = openai.Embedding.create(
                input=[input_text1, input_text2],
                engine=self.engine
            )
            embedding_a = resp['data'][0]['embedding']
            embedding_b = resp['data'][1]['embedding']

            similarity_score = np.dot(embedding_a, embedding_b)
            return similarity_score

        except Exception as e:
            print('Error:', e)
            return