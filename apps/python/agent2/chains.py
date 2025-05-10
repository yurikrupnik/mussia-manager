import datetime

from dotenv import load_dotenv

load_dotenv()

from langchain_core.output_parsers.openai_tools import (
  JsonOutputKeyToolsParser,
  PydanticToolsParser,
)

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

actor_prompt_template = ChatPromptTemplate.from_messages(
  [
    (
      "system",
      """You are expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to research information and improve your answer."""
    ),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Answer the user's question above using the required format."),
  ],
).partial(
  time=lambda: datetime.datetime.now().isoformat(),
)
