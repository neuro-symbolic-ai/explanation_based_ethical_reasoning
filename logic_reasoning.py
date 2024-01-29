import json
from tqdm import tqdm
import pandas as pd
from models.SemanticPrompting import SemanticPrompting
from models.Autoformalization import Autoformalization
from models.WeakRules import WeakRulesGenerator
from models.Filter import Filter
from models.AbductiveInference import AbductiveInference
from models.DeductiveInference import DeductiveInference
from program import SprologRunner
import argparse
import time
import os

class Config:
    def __init__(self, config_file):
        with open(config_file) as f:
            config = json.load(f)
        self.api_key = config['API_KEY']
        self.data_file = config['DATA_FILE']
        self.max_iterations = config['MAX_ITERATIONS']
        self.chat_engine = config['CHAT_ENGINE']
        self.embedding_engine = config['EMBEDDING_ENGINE']
        self.entity_tnorm = config['ENTITY_TNORM']
        self.predicate_tnorm = config['PREDICATE_TNORM']
        self.min_depth = config['MIN_DEPTH']
        self.min_bs_size = config['MIN_BS_SIZE']
        self.lambda_cut = config['LAMBDA_CUT']
        self.max_depth = config['MAX_DEPTH']

class LogicExplainer:
    def __init__(self, config):
        self.config = config
        self.semantic_inference_model = SemanticPrompting(self.config.api_key, self.config.chat_engine)
        self.autoformalization_model = Autoformalization(self.config.api_key, self.config.chat_engine)
        self.abductive_inference_model = AbductiveInference(self.config.api_key, self.config.chat_engine)
        self.deductive_inference_model = DeductiveInference(self.config.api_key, self.config.chat_engine)
        self.filter_model = Filter(self.config.api_key, self.config.embedding_engine)
        self.weak_rules_generator = WeakRulesGenerator()
        self.sprolog = SprologRunner()
    
    def semantic_inference(self,statement, agent, action, patient, args):
        semantic_inference_results = self.semantic_inference_model.inference(statement, agent, action, patient, args)
        return semantic_inference_results
    
    def autoformalization(self, explanatory_chain, iteration, q_id):
        autoformalization_results = self.autoformalization_model.transfer(explanatory_chain, iteration, q_id)
        return autoformalization_results
    
    def abductive_inference(self,statement, agent, action, patient, args, explanaotry_chain, hypothesis):
        abductive_inference_results = self.abductive_inference_model.get_missing_facts(statement, agent, action, patient, args, explanaotry_chain, hypothesis)
        return abductive_inference_results
    
    def deductive_inference(self,statement, agent, action, patient, args, explanaotry_chain):
        deductive_inference_results = self.deductive_inference_model.deductive_inference(statement, agent, action, patient, args, explanaotry_chain)
        return deductive_inference_results
    
    def filter_out_redundant(self, proof_chain, explanatory_chain):
        explanatory_chain_results = self.filter_model.filter_redundant_explanations(proof_chain, explanatory_chain)
        return explanatory_chain_results
            
    def validate_proof_chain(self, proof_chain):
        if proof_chain != '':
            hypothesis = proof_chain[:proof_chain.find('(')]
            if hypothesis.count('_') > 1:
                hypothesis = hypothesis[:hypothesis.index('_', hypothesis.index('_') + 1)]
            proof = proof_chain
        else:
            print('No proof constructed')
            hypothesis = 'none'
            proof = 'none'
        return hypothesis, proof
    
    def update_results(self, results, results_file_path, statement, q_id, iterations, result):
        if f"{q_id}: {statement}" not in results:
            results[f"{q_id}: {statement}"] = {}
        iteration_key = f"{iterations}it"
        
        if iteration_key not in results[f"{q_id}: {statement}"]:
            results[f"{q_id}: {statement}"][iteration_key] = []

        results[f"{q_id}: {statement}"][iteration_key].append(result)

        with open(results_file_path, 'w') as json_file:
            json.dump(results, json_file, indent=4)

    
    def logic_explainer_main(self):
        data = pd.read_csv(f"./data/{self.config.data_file}", index_col=False)
        
        data_file_name, _ = os.path.splitext(self.config.data_file)
        results_file_path = f'./results/{data_file_name}/results.json'
        if os.path.exists(results_file_path):
            with open(results_file_path, 'r') as json_file:
                results = json.load(json_file)
        else:
            results = {}
            os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
            with open(results_file_path, 'w') as json_file:
                json.dump(results, json_file)
        
        
       

        for i, row in enumerate(tqdm(data.itertuples(), total=len(data))):
            statement = row.question
            agent = row.agents
            patient = row.patients
            action = row.actions
            arg = row.arguments
            q_id = int(row.q_id.split('_')[1])
            
            
            print("---------------------------------------------")
            print(f'Current is question {q_id}')
            print(f'Moral scenerio: {statement}')
            
            #semantic inference to get initial explanations and hypothesis
            semantic_hypothesis, semantic_explanatory_chain = self.semantic_inference(statement,agent,patient,action,arg)
            print("---------------------------------------------")
            print(f'Semantic Prompting Explanatory Chain: {semantic_explanatory_chain}\n')
            print(f'Semantic Prompting Hypothesis: {semantic_hypothesis}')
            print("---------------------------------------------")
            
            
            validity = False
            non_redundant = False
            iterations = 0
            explanatory_chain = semantic_explanatory_chain
            hypothesis = f'violate_{semantic_hypothesis.lower()}'
            solver_explanatory_chain = ''
            solver_hypothesis = ''
            
            while not validity and not non_redundant and iterations < self.config.max_iterations:
                explanatory_chain_gold = ''
                #transfer the inferred explanatory sentences into formal format
                self.autoformalization(explanatory_chain, iterations, q_id)
                
                #calculate the weak unification score and construct the weak rules with existing facts and transferred rules
                self.weak_rules_generator.get_weak_rules(agent, patient, action, arg, q_id, iterations)
                
                #use sprolog to validate the explanaotry sentneces 
                start = time.time()
                proof_chain,proof_score,full_chain = self.sprolog.run_sprolog(self.config.entity_tnorm, self.config.predicate_tnorm, self.config.min_depth, self.config.min_bs_size, self.config.lambda_cut, self.config.max_depth,q_id,iterations)
                print('Running time:'+str(time.time()-start))
                solver_hypothesis, solver_proof = self.validate_proof_chain(proof_chain)
                print(f'The proof chain at iteration {iterations} is: {solver_proof}')
                print(f'The hypothesis inferred from solver at iteration {iterations} is: {solver_hypothesis}')
                if solver_proof != 'none':
                    solver_explanatory_chain = self.filter_out_redundant(solver_proof,explanatory_chain)
                else:
                    solver_explanatory_chain = 'none'
                print(f'The explanatory chain inferred from solver at iteration {iterations} is: {solver_explanatory_chain}')
                print("---------------------------------------------")
                
                if hypothesis == solver_hypothesis:
                    validity = True
                    if all(item.strip().lower() in solver_explanatory_chain.lower() for item in explanatory_chain.split('.')):
                        non_redundant = True
                    explanatory_chain_gold = solver_explanatory_chain
                    result = {
                        "hypothesis": hypothesis,
                        "solver_hypothesis": solver_hypothesis,
                        "proof_chain": solver_proof,
                        "explanatory_chain": explanatory_chain,
                        "validity": validity,
                        "non-redundant": non_redundant,
                        "gold_explanatory_chain": explanatory_chain_gold
                    }
                    self.update_results(results,results_file_path,statement,q_id,iterations,result)        
                    break
                else:
                    explanatory_chain = '. '.join([item.strip() for item in explanatory_chain.lower().split('.') if item.strip() not in solver_explanatory_chain.lower().split('.')]) 
                    new_explanatory_chain = self.abductive_inference(statement,agent,action,patient,arg,explanatory_chain,hypothesis)
                    new_hypothesis = self.deductive_inference(statement,agent,action,patient,arg,new_explanatory_chain)
                    print(f"\nNew hypothesis inferred from deductive inference: {hypothesis}")
                    print("---------------------------------------------")
                    result = {
                        "hypothesis": hypothesis,
                        "new hypothesis": new_hypothesis,
                        "solver_hypothesis": solver_hypothesis,
                        "proof_chain": solver_proof,
                        "explanatory_chain": explanatory_chain,
                        "new_explanatory_chain": new_explanatory_chain,
                        "validity": validity,
                        "non-redundant": "null",
                        "gold_explanatory_chain": " "
                    }
                    
                    self.update_results(results,results_file_path,statement,q_id,iterations,result) 
                    explanatory_chain = new_explanatory_chain
                    hypothesis = new_hypothesis             
                    iterations += 1
                   
            
                    
            
                        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the logic explainer.')
    parser.add_argument('-data', type=str, help='The data file name')
    args = parser.parse_args()

    config = Config('config.json')
    config.data_file = args.data  
    logic_explainer = LogicExplainer(config)
    logic_explainer.logic_explainer_main()