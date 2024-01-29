import openai
import tenacity

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