from models.WeakUnification import WeakUnification


class DataProcessor:
    def __init__(self):
        self.chars = ["'s", '?', ',','(',')','[',']','-',"n't","'d","'m"]

    def process_string(self, string):
        for char in self.chars:
            if char == "n't":
                string = string.replace(char,'not').lstrip().lower()
            else:
                string = string.replace(char,'').lstrip().lower()
        return ' '.join(string.split())

    def split_string(self, string):
        if isinstance(string, float):
            string = str(string)
        return string.split(',')

    def process_data(self, action, agent, patient, argument):
        action_list = [self.process_string(a) for a in self.split_string(action)]
        agent_list = [self.process_string(a) if a not in ["i","I"] else '' for a in self.split_string(agent)]
        patient_list = [self.process_string(p) for p in self.split_string(patient)]
        argument_list = [self.process_string(arg) for arg in self.split_string(argument)]

        return action_list, agent_list, patient_list, argument_list

class WeakRulesGenerator:
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.weak_unification = WeakUnification()
        print("WeakRulesGenerator initialised.")
        
    def get_weak_rules(self, agent, patient, action, argument, q_id, iteration):
        action_list, agent_list, patient_list, argument_list = self.data_processor.process_data(action, agent, patient, argument)
        
        prolog_transferred_rule_list = []
        with open(f'./kb/rules/question_{q_id}/{iteration}it.txt', 'r') as readfile:
            prolog_transferred_rule_list = [item.split('.')[0] for item in readfile.readlines()]
       
        self.weak_unification.create_rule(prolog_transferred_rule_list,agent_list,action_list,patient_list,argument_list,q_id,iteration)
        