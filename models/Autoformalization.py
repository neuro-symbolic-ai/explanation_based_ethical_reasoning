from models.utils import OpenAIModel
import re
import os

class Autoformalization:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.prompts_file = './prompts/Autoformalization.txt'
        self.model = OpenAIModel(self.api_key, self.engine)
    
    def replace_content(self, content, replacements):
        return re.sub('|'.join(re.escape(str(k)) for k in replacements), lambda m: str(replacements[m.group(0)]), content)

    def process_prompts(self, explanatory_chain):
        with open(self.prompts_file, 'r') as prompts_file:
            content = prompts_file.read()
            
        replacements = {
            '{{explanatory chain}}': explanatory_chain
        }
        content = self.replace_content(content, replacements)
        
        system_prompt, user_prompt = map(str.strip, content.split('USER: '))
        system_prompt = system_prompt.replace('SYSTEM: ', '')
        
        return system_prompt, user_prompt

    def transfer(self, explanatory_chain, iterations, q_id):
        system_prompt, user_prompt = self.process_prompts(explanatory_chain)
        for _ in range(10):
            result_list = []
            inference_result = self.model.chat(system_prompt, user_prompt)
            if "=" in inference_result:
                result_lines = inference_result.split('\n')
                result_list = [re.sub(r'^\d+\.\s*', '', line) for line in result_lines if line.strip()]
                break
            
        directory = os.path.join('./kb/rules', f'question_{q_id}')
        os.makedirs(directory, exist_ok=True)

        with open(os.path.join(directory, f'{iterations}it.txt'), 'w') as f:
            f.write('\n'.join(result_list))
        