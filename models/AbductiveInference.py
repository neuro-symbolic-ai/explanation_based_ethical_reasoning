from models.utils import OpenAIModel
import re

class AbductiveInference:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.prompts_file = './prompts/AbductiveInference.txt'
        self.model = OpenAIModel(self.api_key, self.engine)
    
    def replace_content(self, content, replacements):
        return re.sub('|'.join(re.escape(str(k)) for k in replacements), lambda m: str(replacements[m.group(0)]), content)

    def process_prompts(self, statement, agent, action, patient, args, explanatory_chain, hypothesis):
        with open(self.prompts_file, 'r') as prompts_file:
            content = prompts_file.read()
            
        replacements = {
            '{{statement}}': statement,
            '{{agent}}': agent,
            '{{action}}': action,
            '{{patient}}': patient,
            '{{args}}': args,
            '{{explanatory_chain}}': explanatory_chain,
            '{{hypothesis}}': hypothesis
            
        }
        content = self.replace_content(content, replacements)
        
        system_prompt, user_prompt = map(str.strip, content.split('USER: '))
        system_prompt = system_prompt.replace('SYSTEM: ', '')
        
        return system_prompt, user_prompt

    def get_missing_facts(self, statement, agent, action, patient, args, explanatory_chain, hypothesis):
        system_prompt, user_prompt = self.process_prompts(statement, agent, action, patient, args, explanatory_chain, hypothesis)
        
        for _ in range(10):
                inference_result = self.model.chat(system_prompt, user_prompt)
                result_lines = inference_result.split('\n')
                if not result_lines[0].startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                    result_lines = result_lines[1:]
                result_list = [re.sub(r'^\d+\.\s*', '', line) for line in result_lines if line.strip()]
                filter_list = [item for item in result_list if 'the norm of' not in item]
                print(inference_result)
                if filter_list:
                    break
                
        explanation_to_write = ' '.join(filter_list)
        return explanation_to_write
        
           