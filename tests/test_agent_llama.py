from llama_cpp import Llama
from LLMAgent.AgentLlama import AgentLlama
from LLMAgent.ToolRegistry import ToolRegistry

from typing import Annotated

import logging
logging.basicConfig(level=logging.INFO)

llm = Llama(
    #model_path="/home/dllama/projects/text-generation-webui/models/mixtral-8x7b-v0.1.Q5_K_M.gguf",
    # model_path="/home/dllama/projects/llama.cpp/models/llama-2-13b-chat.Q6_K.gguf",
    model_path="/home/dllama/projects/text-generation-webui/models/Llama-3-Yggdrasil-2.0-8B-Q8_0.gguf",

    # chat_format="llama-2",
    # chat_format="chatml-function-calling",

    n_gpu_layers=-1, # Uncomment to use GPU acceleration
)

agent = AgentLlama(llm)

def get_current_date()->dict:
    """
    Get the date for today
    """
    return {
        "year":2024,
        "month":12,
        "day":24,
    }

def is_holiday(
    month: Annotated[int, 'Month of the date', True],
    day  : Annotated[int, 'Day of the date'  , True],
) -> bool:
    """
    Check if date is a holiday
    """
    if month==12 and day in  [24,25]:
        return False # workday for santa
    return True
        

toolbox = ToolRegistry("toolbox")
toolbox.register_func(get_current_date)    
toolbox.register_func(is_holiday)

result = agent.act("Is tomorrow a holiday?", toolbox)
print(result)