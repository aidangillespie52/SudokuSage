from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field
from backend.utils import load_prompt

class HintExtraction(BaseModel):
    r: int = Field(..., description="1-based row index of the cell changed")
    c: int = Field(..., description="1-based column index of the cell changed")
    value: int = Field(..., description="Digit placed in the cell (1-9)")
    method_used: str = Field(
        default="Unknown",
        description="Short name of solving technique"
    )


# cheap small model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

structured_llm = llm.with_structured_output(
    HintExtraction,
    method="function_calling",
)

def extract_hint_fields(chatgpt_response: str) -> HintExtraction:
    template = load_prompt("parse_hint.md")
    full_prompt = template.replace("<<<HINT_TEXT>>>", chatgpt_response)

    return structured_llm.invoke(full_prompt)