import jinja2
from llama_cpp import Llama
import llama_cpp.llama as llama
import llama_cpp.llama_types as llama_types
import llama_cpp.llama_grammar as llama_grammar

import LLMAgent
from LLMAgent.IAgent import *

import json

import logging
logger = logging.getLogger(__name__)


def print_completion(completion):
    print("==COMPLETION=============================================")
    print(completion)
    print("=========================================================")

class AgentLlama(IAgent):
    def __init__(self, llm : llama.Llama,) -> None:
        super().__init__()

        self.llm = llm

        with open(f"{LLMAgent.ROOT}/AgentLlama_Llama3_Instruct.jinja") as f: 
            template = f.read()

            self.template_renderer = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=jinja2.select_autoescape(["html", "xml"]),
                undefined=jinja2.StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True
            ).from_string(template)

    def act(self, 
            situation:str, 
            toolRegistry           : Optional[ToolRegistry] = None,
            toolUseCount           : ToolUseCount = ToolUseCount.AUTO,
            use_internal_reasoning : bool = True
            ):
        logger.info("====================================")
        logger.info(toolRegistry.get_tool_descriptions())

        function_specs         = toolRegistry.get_tool_descriptions()

        prompt = self.template_renderer.render(
            character_description  = "You are a helpful AI assistant.",
            use_internal_reasoning = use_internal_reasoning,
            function_specs         = function_specs,
            user_query             = situation
        )

        print(prompt)

        for round in range(10):
            response_type = self.pick_response_type(prompt, use_internal_reasoning, function_specs)
            
            prompt += "\n"
            prompt += f"{response_type}:"

            if response_type in  ["internal reasoning", "message"]:
                completion = self.llm.create_completion(prompt, max_tokens=None, stop=["\n"])
                print_completion(completion)
                prompt += completion["choices"][0]["text"]

            elif "function." in response_type:
                function_picked = response_type.split(".")[1]  # function.is_holiday -> is_holiday
                function_picked = next( fs for fs in function_specs if fs["function"]["name"]==function_picked)

                grammar = llama_grammar.LlamaGrammar.from_json_schema(
                    json.dumps(function_picked["function"]["parameters"])
                )

                completion = self.llm.create_completion(prompt, max_tokens=None, stop=["\n"], grammar=grammar)
                print_completion(completion)
                function_args = completion["choices"][0]["text"]
                function_reply = toolRegistry.dispatch_func(function_picked["function"]["name"], json.loads(function_args))

                prompt +=  function_args
                prompt +=  "\n"
                prompt += f"reply.{function_picked["function"]["name"]}:"
                prompt += function_reply
                prompt +=  "\n"

            if response_type in  ["message"]:
                break
        
        # response["choices"][0]["text"][len("functions.") :]

        return prompt
    


    def pick_response_type(self, prompt, use_internal_reasoning, function_specs):
        
        response_types = ["message"]
        if use_internal_reasoning: response_types.append("internal reasoning")
        for function_spec in function_specs:
            response_types.append(f"function.{function_spec["function"]["name"]}")
        response_types = " | ".join([f'"{rt}"' for rt in response_types])

        grammar = f'root ::= ({response_types})'
        grammar = llama_grammar.LlamaGrammar.from_string(grammar)

        completion = self.llm.create_completion(prompt, stop=[":"], grammar=grammar)
        print_completion(completion)
        response_type = completion["choices"][0]["text"]

        return response_type