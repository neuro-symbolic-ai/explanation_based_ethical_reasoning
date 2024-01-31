"""
This code is based on the work of L. Weber, P. Minervini, J. Münchmeyer, U. Leser, and T. Rocktäschel.
"NLProlog: Reasoning with Weak Unification for Question Answering in Natural Language." ACL 2019, Florence, Italy.
From: https://github.com/leonweber/nlprolog
"""

import logging
import subprocess
import shlex
import os

class SprologRunner:
    def __init__(self):
        self.BASE_PATH = os.path.dirname(os.path.abspath(__file__))
        logging.basicConfig(level=logging.ERROR)
        self.DEBUG = False

    def get_goal(self):
        with open('./kb/goals.txt', 'r') as file:
            goals = file.read().splitlines()
        return '|'.join(goals)

    def query(self, goal, entity_tnorm, predicate_tnorm, min_depth, min_bs_size, lambda_cut, max_depth, q_id, iteration_times):
        lambda_cut = "|".join([str(lambda_cut)] * len(goal.split('|')))
    
        cmd = f'{self.BASE_PATH}/spyrolog {self.BASE_PATH}/kb/prolog_kb/question_{q_id}/{iteration_times}it.txt {self.BASE_PATH}/kb/sims.txt {goal} {max_depth} {lambda_cut} {entity_tnorm}|{predicate_tnorm} {min_bs_size}'
        cmd = shlex.split(cmd)
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        except (subprocess.TimeoutExpired, ValueError):
            return [[0, 0, '', ''] for _ in goal.split('|')]
        logging.debug("spyrolog stdout: " + result.stdout.decode())
        logging.debug("spyrolog stderr: " + result.stderr.decode())
        results = []    
        try:
            for r in result.stdout.split(b'\n'):
                if len(r) == 0:
                    continue
                split = r.split(b' ')
                if len(split) < 3:
                    results.append( [float(split[0]), int(split[1]), '', ''] )
                else:
                    results.append( [float(split[0]), int(split[1]), b' '.join(split[3:]).decode(), split[2].decode()] )
            return results
        except ValueError:
            raise RuntimeError(result.stderr)

    def run_sprolog(self, entity_tnorm, predicate_tnorm, min_depth, min_bs_size, lambda_cut, max_depth, q_id, iteration_times):
        goal = self.get_goal()
        result = self.query(goal, entity_tnorm, predicate_tnorm, min_depth, min_bs_size, lambda_cut, max_depth,q_id, iteration_times)
        ans = {}
        current_score = 0
        try:
            for i, (score, depth, rule, unification) in enumerate(result):
                #print('score: '+ str(score))
                #print('depth: '+ str(depth))
                #print('rule: '+ rule)
                #print('unification: '+ str(unification))
                if score > current_score:
                    current_score = score
                ans[rule] = score
            return max(ans, key=ans.get),current_score,result
        except ValueError:
            return '',0.0,''



    
    
 
    
