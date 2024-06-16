# About
A simple LLM agent that can call functions to help with its task.

- Use locally run llama-cpp-python
- GBNF gramma is used to ensure LLM output correct arguments for the functions
- Funcs are called and results are fed back to LLM, all automatically without human in the loop

# Install
git clone https://github.com/ylchan87/LLMAgent.git
cd LLMAgent
python3 -m pip install -e .

# Run
```
cd LLMAgent/test

# edit the path to weight file first, onlt tested with Llama3 instruct model and its variants
python3 test_agent_llama.py  
```