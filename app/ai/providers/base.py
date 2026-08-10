from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str = None) -> str:
        """Generate simple text response from the model."""
        pass

    @abstractmethod
    def generate_structured_output(
        self, 
        prompt: str, 
        response_model: Type[T], 
        system_instruction: str = None
    ) -> T:
        """Generate validated structured output parsed into a Pydantic model."""
        pass
