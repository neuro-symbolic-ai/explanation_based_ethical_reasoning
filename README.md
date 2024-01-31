# Enhancing Ethical Explanations of Large Language Models through Iterative Symbolic Refinement 

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

