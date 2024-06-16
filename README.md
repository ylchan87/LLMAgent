# About
A simple LLM agent that can call functions to help with its task.

- Use locally run llama-cpp-python
- GBNF gramma is used to ensure LLM output correct arguments for the functions
- Funcs are called and results are fed back to LLM, all automatically without human in the loop

# Install
```
git clone https://github.com/ylchan87/LLMAgent.git
cd LLMAgent
python3 -m pip install -e .
```

# Run
```
cd LLMAgent/test

# edit the path to weight file first, onlt tested with Llama3 instruct model and its variants
python3 test_agent_llama.py  
```

In a _lucky_ run, you would get output like this:
```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a helpful AI assistant.

You response to user query must end in a single message with the following format:

message:
<message>

Before the message, you could note down zero or more internal thoughts, with the following format:

internal reasoning:
<internal reasoning>


Before the message, you could make zero or more function calls to help with your tasks. Functions are called with the following format:

functions.<function_name>:
{ "arg1": "value1", "arg2": "value2" }

the function would then reply in following format:

reply.<function_name>:
{ "arg1": "value1", "arg2": "value2" }

You only have access to the following functions:

{"function": {"description": "Get the date for today", "name": "get_current_date", "parameters": {"properties": {}, "required": [], "type": "object"}}, "type": "function"}
{"function": {"description": "Check if date is a holiday", "name": "is_holiday", "parameters": {"properties": {"day": {"description": "Day of the date", "type": "integer"}, "month": {"description": "Month of the date", "type": "integer"}}, "required": ["month", "day"], "type": "object"}}, "type": "function"}

Use reply from function calls whenever they are applicable.


Think step by step and reply the user's query.

<|eot_id|>
<|start_header_id|>user<|end_header_id|>
Is tomorrow a holiday?<|eot_id|><|start_header_id|>assistant<|end_header_id|>
internal reasoning: To determine if tomorrow is a holiday, I will first get today's date, then check if that day falls on any known holiday.
function.get_current_date:{ } 
reply.get_current_date:{'year': 2024, 'month': 12, 'day': 24}

function.is_holiday:{"month": 12, "day": 24} 
reply.is_holiday:False

message: No, tomorrow (December 25th, 2024) is not a holiday.
```

Note the `is_holiday` func is delibarately set to defy common knowledge in order to test the LLM.