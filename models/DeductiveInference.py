from models.utils import OpenAIModel
import re

class DeductiveInference:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.prompts_file = './prompts/DeductiveInference.txt'
        self.model = OpenAIModel(self.api_key, self.engine)
    
    def replace_content(self, content, replacements):
        return re.sub('|'.join(re.escape(str(k)) for k in replacements), lambda m: str(replacements[m.group(0)]), content)

    def process_prompts(self, statement, agent, action, patient, args, explanatory_chain):
        with open(self.prompts_file, 'r') as prompts_file:
            content = prompts_file.read()
            
        replacements = {
            '{{statement}}': statement,
            '{{agent}}': agent,
            '{{action}}': action,
            '{{patient}}': patient,
            '{{args}}': args,
            '{{explanatory_chain}}': explanatory_chain,
        }
        content = self.replace_content(content, replacements)
        
        system_prompt, user_prompt = map(str.strip, content.split('USER: '))
        system_prompt = system_prompt.replace('SYSTEM: ', '')
        
        return system_prompt, user_prompt

    def deductive_inference(self, statement, agent, action, patient, args, explanatory_chain):
        system_prompt, user_prompt = self.process_prompts(statement, agent, action, patient, args, explanatory_chain)
        
        for _ in range(10):
            inference_result = self.model.chat(system_prompt, user_prompt)
            if "It violates the norm of" in inference_result:
                norm_violated = re.search("It violates the norm of (.+?)\.", inference_result).group(1)
                hypothesis = f"violate_{norm_violated.lower().strip()}"
                return hypothesis
        
        return ''
        
        
           