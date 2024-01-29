import numpy as np
import gensim.downloader as api
from scipy import spatial
import os

class WeakUnification:
    def __init__(self,model_name="glove-wiki-gigaword-300", threshold=0.5):
        print("Initialising WeakUnification...")
        self.model = api.load(model_name)
        self.threshold = threshold
        print("WeakUnification initialised.")
        
    def split_into_words(self, sentence):
        return sentence.lower().split()

    def get_sentence_vector(self, sentence):
        return np.mean([self.model[i] for i in self.split_into_words(sentence)], axis=0)

    def calculate_cosine_similarity(self, sentence1, sentence2):
        try:
            return 1 - spatial.distance.cosine(self.get_sentence_vector(sentence1), self.get_sentence_vector(sentence2))
        except ValueError:
            return 0
            
            
    def process_role_list(self, list_to_process, predicates_to_calculate, predicate_index):
        for list_index in range(len(list_to_process)):
            if list_to_process[list_index] not in ['None','','none']:
                s1 = self.calculate_cosine_similarity(list_to_process[list_index],predicates_to_calculate[predicate_index])                  
                if s1 >= self.threshold:
                    arg1 = predicates_to_calculate[predicate_index].replace(' ','_')+ '(X) :- '
                    arg2 = list_to_process[list_index].replace(' ','_')+'(X)'
                    sim_temp = arg1+arg2+'. = '+str(s1)
                    return sim_temp
                
    def process_list(self, list_to_process, current_value):
        for j in range(len(list_to_process)):
            if list_to_process[j] not in ['None','','none']:
                s1 = self.calculate_cosine_similarity(list_to_process[j],current_value)
                if s1 >=self.threshold:
                    arg1 = current_value.replace(' ','_')+ '(X) :- '
                    arg2 = list_to_process[j].replace(' ','_')+'(X)'
                    sim_temp = arg1+arg2+'. = '+str(s1)
                    return sim_temp
                
        
    def create_rule(self,prolog_transferred_rule_list,agent_list,action_list,patient_list,args_list,q_id,iteration_times):
    
        transferred_rules_to_write =[]
        facts_to_write =[]
        weak_rules_to_write = []
        predicates_to_calculate = []
        head_body_dic = {}
        principles = ['physical harm', 'animal', 'emotional harm', 'human', 'cheating','free riding','deception','threat reputation','in competition',
                    'disobedience','traditional authority','disrespect','symbol of authority', 'identifiable member',
                    'deviant','sex','degrading','disgusting','dirty','reduce freedom','restrict autonomy']
        similarity_to_write = []

        transferred_rules_to_write = list(set([
            rule + ". = 1.0" for rule in prolog_transferred_rule_list if len(rule) - rule.find('-') > 2
        ]))
    
        for i, sentence_temp in enumerate(prolog_transferred_rule_list):
            if ':-' in sentence_temp:
                first_arg_index = sentence_temp.find('X')
                second_arg_index = sentence_temp.find(':-')
                first_arg = sentence_temp[:first_arg_index-1]
                second_arg = sentence_temp[second_arg_index+3:]
                if ',' in second_arg:
                    args = second_arg.split(',')
                    arg2_index = args[0].find('X')
                    arg2 = args[0][:arg2_index-1]
                    arg1 = first_arg.replace('_', ' ')
                    arg2 = arg2.replace('_', ' ')
                    head_body_dic.update({arg1:arg2})
                    for _, arg in enumerate(args[1:], start=1):
                        remained = arg[:-3].lstrip()
                        predicates_to_calculate.append(remained.replace('_', ' '))
                    predicates_to_calculate.append(arg1)
                else:
                    arg2_index = second_arg.find('X')
                    arg2 = second_arg[:arg2_index-1]
                    arg1 = first_arg.replace('_', ' ')
                    arg2 = arg2.replace('_', ' ')
                    head_body_dic.update({arg1:arg2})
            
        
        for predicate_index in range(len(predicates_to_calculate)-1):
            try:
                for list_to_process in [action_list, patient_list, args_list, agent_list]:
                    sim_temp = self.process_role_list(list_to_process, predicates_to_calculate, predicate_index)
                    if sim_temp:
                        weak_rules_to_write.append(sim_temp)
            except KeyError:
                continue
                            
                            
        for current_key,current_value in head_body_dic.items():
        
            try:
                for idx in range(len(principles)):
                    similarity = self.calculate_cosine_similarity(current_key,principles[idx])
                    #print(similarity)
                    #print('for '+principles[j]+' ----- '+current_key)
                    if similarity >= self.threshold and similarity != 1:
                        arg1 = principles[idx].replace(' ','_')+ '(X) :- '
                        arg2 = current_key.replace(' ','_')+ '(X)'
                        sim_temp = arg1+arg2+'. = '+str(similarity)
                        
                        
                        arg1_sim = principles[idx].replace(' ','_')
                        arg2_sim = current_key.replace(' ','_')
                        
                        similarity_to = arg1_sim+' ~ '+arg2_sim+' = '+str(similarity)
                        
                        weak_rules_to_write.append(sim_temp)
                        similarity_to_write.append(similarity_to)
                    
                for other_key,other_value in head_body_dic.items():
                    if current_key!=other_key:
                        similarity = self.calculate_cosine_similarity(current_key,other_value)
                        
                    if similarity !=1 and similarity>=self.threshold:
                        if current_key != '' and other_value != '':
                            arg1 = other_value.replace(' ','_')+ '(X) :- '
                            arg2 = current_key.replace(' ','_')+ '(X)'
                            sim_temp = arg1+arg2+'. = '+str(similarity)
                            
                            duplicate = arg1+arg2
                            #print(duplicate)
                            if list(filter(lambda x: duplicate in x, transferred_rules_to_write)):
                                print('exist')
                            else:
                                weak_rules_to_write.append(sim_temp)
                                
                for idx in range(len(predicates_to_calculate)-1):
                    if current_key not in predicates_to_calculate:
                        similarity = self.calculate_cosine_similarity(current_key,predicates_to_calculate[idx])
                        #print(similarity)
                        #print('for '+predicates_to_calculate[j]+' ----- '+current_key)
                        if similarity >= self.threshold and similarity != 1:
                            arg1 = predicates_to_calculate[idx].replace(' ','_')+ '(X) :- '
                            arg2 = current_key.replace(' ','_')+ '(X)'
                            sim_temp = arg1+arg2+'. = '+str(similarity)
                            
                            weak_rules_to_write.append(sim_temp)
                            
                for list_to_process in [action_list, patient_list, args_list, agent_list]:
                    sim_temp = self.process_list(list_to_process, current_value)
                    if sim_temp:
                        weak_rules_to_write.append(sim_temp)

            except KeyError:
                continue
            except ValueError:
                continue
       
            
        roles_lists = [action_list, patient_list, args_list, agent_list]
        for list_to_process in roles_lists:
            for i in range(len(list_to_process)):
                if list_to_process[i] not in ['None','','none']:
                    facts_to_write.append(list_to_process[i].replace(' ','_')+'(X). = 1.0')
                
        
        
        initial_facts = [f"{line}\n" for line in facts_to_write]
        weak_rules = [f"{line}\n" for line in weak_rules_to_write]
        transferred_rules = [f"{line}\n" for line in transferred_rules_to_write]

        all_contents = {
            'initial_facts.txt': initial_facts,
            'weak_rules.txt': weak_rules,
            'transferred_rules.txt': transferred_rules,
        }

        filenames = ['kb/principles.txt', 'transferred_rules.txt', 'weak_rules.txt', 'initial_facts.txt']
        
        directory = os.path.join('./kb/prolog_kb', f'question_{q_id}')
        os.makedirs(directory, exist_ok=True)

        unique_lines = set()
        for fname in filenames:
            if fname in all_contents:
                unique_lines.update(all_contents[fname])
            else:
                with open(fname) as infile:
                    unique_lines.update(infile.readlines())

        with open(os.path.join(directory, f'{iteration_times}it.txt'), 'w') as outfile:
            outfile.writelines(unique_lines)

        with open('kb/sims.txt', 'w') as f:
            for line in similarity_to_write:
                f.write(f"{line}\n")