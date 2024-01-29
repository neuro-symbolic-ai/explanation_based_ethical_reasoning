from models.utils import OpenAIModel


class Filter:
    def __init__(self, api_key, engine):
        self.api_key = api_key
        self.engine = engine
        self.model = OpenAIModel(self.api_key, self.engine)
    
    def parse_proof_chain(self,proof_chain_list):
        new_list = []
        for item in proof_chain_list:
            if ":-" in item:
                before, after = item.split(":-")
                new_list.append(before.replace(" ", ""))
                new_list.append(after.replace(" ", ""))
            else:
                new_list.append(item.replace(" ", ""))
        return new_list

    def filter_redundant_explanations(self, proof_chain, explanatory_chain):
        explanation_to_write = ''
        proof_chain_remove_unification_score = [x for x in proof_chain.split("|") if not x.replace('.','').isdigit()][2:]
        ans = self.parse_proof_chain(proof_chain_remove_unification_score)
        
        outer_inforamtion = ['physical_harm(X)', 'animal(X)', 'emotional_harm(X)', 'human(X)', 'cheating(X)','free_riding(X)','deception(X)','threat_reputation(X)','in_competition(X)',
                            'disobedience(X)','traditional_authority(X)','disrespect(X)','symbol_of_authority(X)', 'identifiable_member(X)',
                            'deviant(X)','sex(X)','degrading(X)','disgusting(X)','dirty(X)','reduce_freedom(X)','restrict_autonomy(X)'
                        ]
        
        removed_abstract_list = [x for x in ans if not any(y in x for y in outer_inforamtion)]
        removed_abstract_list = ans
        proof_sentences = list(set(removed_abstract_list))
        keyword_facts = [word for phrase in proof_sentences for word in phrase.replace('(',' ').replace(')',' ').split() if word != 'X']
        filtered_facts = [item for item in keyword_facts if item != '.']
        
        inferred_sentences = explanatory_chain.split('.')[:-1]
        inferred_sentences = [sentence.lstrip().lower() for sentence in inferred_sentences]
        used_explanation = []
        for i in range(len(filtered_facts)):
            current_similarity_score = 0
            to_add = ''
            for j in range(len(inferred_sentences)):
                similarity_score = self.model.calculate_similarity(filtered_facts[i],inferred_sentences[j])
                if similarity_score is not None and similarity_score > current_similarity_score :
                    to_add = inferred_sentences[j]
                    current_similarity_score = similarity_score
            used_explanation.append(to_add)
            
        used_explanation = set(used_explanation)
        explanation_to_write = '. '.join(used_explanation)+'.'
        return explanation_to_write
 