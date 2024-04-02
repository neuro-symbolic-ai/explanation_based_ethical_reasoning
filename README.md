# Enhancing Ethical Explanations of Large Language Models through Iterative Symbolic Refinement 
An increasing amount of research in Natural Language Inference (NLI) focuses on the application and evaluation of Large Language Models (LLMs) and their reasoning capabilities. Despite their success, however, LLMs are still prone to factual errors and inconsistencies in their explanations, offering limited control and interpretability for inference in complex domains. In this paper, we focus on ethical NLI, investigating how hybrid neuro-symbolic techniques can enhance the logical validity and alignment of ethical explanations produced by LLMs. Specifically, we present an abductive-deductive framework named Logic-Explainer, which integrates LLMs with an external backward-chaining solver to refine step-wise natural language explanations and jointly verify their correctness, reduce incompleteness and minimise redundancy. An extensive empirical analysis demonstrates that Logic-Explainer can improve explanations generated via in-context learning methods and Chain-of-Thought (CoT) on challenging ethical NLI tasks, while, at the same time, producing formal proofs describing and supporting models' reasoning. As ethical NLI requires commonsense reasoning to identify underlying moral violations, our results suggest the effectiveness of neuro-symbolic methods for multi-step NLI more broadly, opening new opportunities to enhance the logical consistency, reliability, and alignment of LLMs.

# Installation
To get the libraries:

```bash
pip install -r requirements.txt
```

# Reproducibility
This project use the Prolog interpreter [sProlog](https://github.com/leonweber/spyrolog) as the neuro-symbolic solver. 

You can set your OPENAI_KEY in `./config.json`

Run:
```bash
python logic_reasoning.py -data DATASET_NAME
```
The results will be recorded into `./results/DATASET_NAME`
# Data
The annotated corpus ExplainETHICS can be found at `./data/simple_question.csv` for easy moral scenarios  and `./data/hard_question.csv` for challenging moral scenarios. 

ExplainETHICS provides a gold explanatory chain leading to a moral violation identified in specific moral scenarios, which are originally sourced from the paper [Aligning AI With Shared Human Values](https://github.com/hendrycks/ethics).
#
If you find this repository useful, please consider citing our paper.
```
@misc{quan2024enhancing,
      title={Enhancing Ethical Explanations of Large Language Models through Iterative Symbolic Refinement}, 
      author={Xin Quan and Marco Valentino and Louise A. Dennis and André Freitas},
      year={2024},
      eprint={2402.00745},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
