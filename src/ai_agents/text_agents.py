from typing import Annotated
from typing_extensions import TypedDict
from uuid import uuid4

from langgraph.graph.message import add_messages

from langchain_core.messages import (
    AIMessage,
    SystemMessage,
)

from src.utils.utils import handle_errors
from src.ai_agents.llm_models import llm_model_openai41_creative
from src.ai_agents.prompts import CUSTOMER_CALL_ASSISTANT


class State(TypedDict):
    thread_id: str = str(uuid4())
    messages: Annotated[list, add_messages]

@handle_errors(default_return={"messages": [AIMessage(content="Sorry, there are some issues on my side. Can you say that again?")]})
async def information_assistant_agent(state: State) -> dict:
    message = state["messages"]
    system_prompt = [SystemMessage(content=CUSTOMER_CALL_ASSISTANT)]
    response = (
        await llm_model_openai41_creative.ainvoke(system_prompt+message)
    )
    return {"messages": [AIMessage(content=response.content)]}