from abc import ABC, abstractmethod
from LLMAgent.ToolRegistry import ToolRegistry
from typing import Optional
from enum import Enum

class ToolUseCount(Enum):
    AUTO        = -1
    FORCED_ZERO =  0
    FORCED_ONCE =  1

class IAgent(ABC):
    @abstractmethod
    def act(situation:str, 
            toolRegistry       : Optional[ToolRegistry] = None,
            toolUseCount       : ToolUseCount = ToolUseCount.AUTO,
            allowInnerThoughts : bool = True
            ):
        """
        situation is a string that could be:
        a scenario          ( You are trapped in a room blah blah blah)
        a problem statement ( One ice cream cost $7, how many you can buy with $20?)
        a line form user    ( User: Hello how are you? )

        it is used to form part of the text prompt passed to LLM
        """
        pass
