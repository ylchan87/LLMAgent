"""
This code is modified from 
https://github.com/THUDM/ChatGLM3/blob/main/tools_using_demo/tool_register.py
"""

import inspect
import traceback
import logging
from copy import deepcopy
from pprint import pformat
from types import GenericAlias
from typing import get_origin, Annotated

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self, name) -> None:
        """
        ref: https://platform.openai.com/docs/api-reference/assistants/createAssistant

        followung openAI, tool could be:
        - code interpreter
        - file search tool
        - function

        we only impl function for now
        """

        self.name = name
        self.reset()

    def reset(self):        
        self._FUNC_HOOKS = {}
        self._FUNC_DESCRIPTIONS = {}

        self._CODE_INTERPRETER_HOOKS = {}
        self._CODE_INTERPRETER_DESCRIPTIONS = {}

        self._FILE_SEARCH_TOOL_HOOKS = {}
        self._FILE_SEARCH_TOOL_DESCRIPTIONS = {}
    
    def register_code_interpreter(self):
        raise NotImplementedError

    def unregister_code_interpreter(self):
        raise NotImplementedError
    
    def register_file_search_tool(self):
        raise NotImplementedError

    def unregister_file_search_tool(self):
        raise NotImplementedError

    def register_func(self, func: callable):
        """
        register_tool and create json in same format that openAI use to describe a func
        ref: https://platform.openai.com/docs/guides/function-calling
        """

        func_name = func.__name__
        if func_name in self._FUNC_HOOKS:
            logger.warn(f"Function {func_name} already registered, would override")

        func_description = inspect.getdoc(func)
        func_description = "" if func_description is None else func_description.strip()

        # this part adhere to the "json-schema" standard
        # ref: https://json-schema.org/learn/getting-started-step-by-step
        func_params = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        python_params = inspect.signature(func).parameters
        for name, param in python_params.items():
            annotation = param.annotation
            if annotation is inspect.Parameter.empty:
                raise TypeError(f"Parameter `{name}` missing type annotation")
            if get_origin(annotation) != Annotated:
                raise TypeError(f"Annotation type for `{name}` must be typing.Annotated")

            typ, (description, required) = annotation.__origin__, annotation.__metadata__
            
            if isinstance(typ, GenericAlias):
                typ = str(typ) # FIXME?: downstream probably cannot convert this to GBNF schema
            elif typ == int:
                typ = "integer" 
            elif typ == float:
                typ = "number" 
            else:
                typ = typ.__name__
            if not isinstance(description, str):
                raise TypeError(f"Description for `{name}` must be a string")
            if not isinstance(required, bool):
                raise TypeError(f"Required for `{name}` must be a bool")

            func_params["properties"][name] = {
                "type": typ,
                "description": description,
                # "enum": ["celsius", "fahrenheit"], # eg from openAI, not impl by us yet
            }

            if required:
                func_params["required"].append(name)

        func_def = {
            "name": func_name,
            "description": func_description,
            "parameters": func_params
        }

        logger.info(f"registered tool {func_name} in registry {self.name}")
        self._FUNC_HOOKS[func_name] = func
        self._FUNC_DESCRIPTIONS[func_name] = func_def

        return func

    def unregister_func(self, func_name: str) -> None:
        if func_name not in self._FUNC_HOOKS:
            logger.warn(f"Cannot unregister function {func_name} as it is absent in registry {self.name}")
            return
        
        del self._FUNC_HOOKS[func_name]
        del self._FUNC_DESCRIPTIONS[func_name]

    def dispatch_func(self, func_name: str, func_params: dict) -> str:
        if func_name not in self._FUNC_HOOKS:
            return f"Tool `{func_name}` not found. Please use a provided tool."
        func = self._FUNC_HOOKS[func_name]
        try:
            ret = func(**func_params)
        except:
            ret = traceback.format_exc()
        return str(ret)  # FIXME what is a better representation of func return value for LLM to understand?

    def get_tool_descriptions(self) -> list:
        tools = []

        for k,v in self._CODE_INTERPRETER_DESCRIPTIONS.items():
            tools.append({
                "type": "code_interpreter",
            })
        
        for k,v in self._FILE_SEARCH_TOOL_DESCRIPTIONS.items():
            tools.append({
                "type": "file_search",
            })

        for k,v in self._FUNC_DESCRIPTIONS.items():
            tools.append({
                "type": "function",
                "function": v,
            })
        
        return tools

    


if __name__ == "__main__":
    registry = ToolRegistry("ToolBox")

    @registry.register_func
    def random_number_generator(
            seed: Annotated[int, 'The random seed used by the generator', True],
            range: Annotated[tuple[int, int], 'The range of the generated numbers', True],
    ) -> int:
        """
        Generates a random number x, s.t. range[0] <= x < range[1]
        """
        if not isinstance(seed, int):
            raise TypeError("Seed must be an integer")
        if not isinstance(range, tuple):
            raise TypeError("Range must be a tuple")
        if not isinstance(range[0], int) or not isinstance(range[1], int):
            raise TypeError("Range must be a tuple of integers")

        import random
        return random.Random(seed).randint(*range)

    @registry.register_func
    def get_weather(
            city_name: Annotated[str, 'The name of the city to be queried', True],
    ) -> str:
        """
        Get the current weather for `city_name`
        """

        if not isinstance(city_name, str):
            raise TypeError("City name must be a string")

        key_selection = {
            "current_condition": ["temp_C", "FeelsLikeC", "humidity", "weatherDesc", "observation_time"],
        }
        import requests
        try:
            resp = requests.get(f"https://wttr.in/{city_name}?format=j1")
            resp.raise_for_status()
            resp = resp.json()
            ret = {k: {_v: resp[k][0][_v] for _v in v} for k, v in key_selection.items()}
        except:
            import traceback
            ret = "Error encountered while fetching weather data!\n" + traceback.format_exc()

        return str(ret)

    print(registry.dispatch_func("get_weather", {"city_name": "beijing"}))
    print(registry.get_tool_descriptions())