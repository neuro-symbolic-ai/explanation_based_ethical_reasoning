from models.utils import OpenAIModel
import re

class SemanticPrompting:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.prompts_file = './prompts/SemanticPrompting.txt'
        self.model = OpenAIModel(self.api_key, self.engine)
    
    def replace_content(self, content, replacements):
        return re.sub('|'.join(re.escape(str(k)) for k in replacements), lambda m: str(replacements[m.group(0)]), content)

    def process_prompts(self, statement, agent, action, patient, args):
        with open(self.prompts_file, 'r') as prompts_file:
            content = prompts_file.read()
            
        replacements = {
            '{{statement}}': statement,
            '{{agent}}': agent,
            '{{action}}': action,
            '{{patient}}': patient,
            '{{args}}': args
        }
        content = self.replace_content(content, replacements)
        
        system_prompt, user_prompt = map(str.strip, content.split('USER: '))
        system_prompt = system_prompt.replace('SYSTEM: ', '')
        
        return system_prompt, user_prompt

    def parse(self, result):
        result = re.sub(".*?Answer:", "", result, flags=re.DOTALL).strip()
        sentences = result.split(". ")
        norm_violated = next((m.group(1) for m in (re.search("norm of (\w+)", s) for s in sentences) if m), None)
        explanatory_chain = '. '.join(s.replace("Answer:", "").strip() for s in sentences if "the norm of" not in s.lower()) + '.'
        norm_violated = str(norm_violated)
        
        return norm_violated, explanatory_chain

    def inference(self, statement, agent, action, patient, args):
        system_prompt, user_prompt = self.process_prompts(statement, agent, action, patient, args)
        for _ in range(10):
            inference_result = self.model.chat(system_prompt, user_prompt)
            print(inference_result)
            if "violates the norm of" in inference_result and "Answer:" in inference_result:
                return self.parse(inference_result)
        
        return '',''