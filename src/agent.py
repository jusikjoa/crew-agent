"""
AI Agent Implementation
LangChain-based AI Agent with custom tools
"""
import os
from typing import List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from tools import WebSearchTool, APICallerTool


# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """You are a helpful AI assistant.
You can use the following tools to help answer questions:
- web_search: Search the web for information
- api_caller: Call external APIs

Use tools when necessary to provide accurate and up-to-date information."""


class CrewAgent:
    """Crew AI Agent Class"""

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        verbose: bool = True,
    ):
        """
        Initialize Agent

        Args:
            model_name: OpenAI model name
            temperature: Temperature (0~1)
            verbose: Verbose output
        """
        self.verbose = verbose

        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
        )

        # Setup tools
        self.tools = self._setup_tools()

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Conversation history
        self.messages: List = [SystemMessage(content=SYSTEM_PROMPT)]

    def _setup_tools(self) -> List[BaseTool]:
        """Setup available tools"""
        tools = [
            WebSearchTool(),
            APICallerTool(),
        ]
        return tools

    def run(self, query: str) -> str:
        """
        Run the agent

        Args:
            query: User query

        Returns:
            Agent response
        """
        try:
            self.messages.append(HumanMessage(content=query))

            # Call LLM with tools
            response = self.llm_with_tools.invoke(self.messages)

            if self.verbose:
                print(f"\nResponse: {response}")

            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_input = tool_call['args']

                    if self.verbose:
                        print(f"\nCalling tool: {tool_name}")
                        print(f"Tool input: {tool_input}")

                    # Find and execute the tool
                    for tool in self.tools:
                        if tool.name == tool_name:
                            if tool_name == "web_search":
                                result = tool._run(tool_input.get('query', ''))
                            elif tool_name == "api_caller":
                                import json
                                result = tool._run(json.dumps(tool_input))
                            else:
                                result = tool._run(str(tool_input))

                            tool_results.append(result)

                            if self.verbose:
                                print(f"Tool result: {result[:200]}...")

                # Add tool results to messages and get final response
                if tool_results:
                    self.messages.append(response)

                    for i, result in enumerate(tool_results):
                        self.messages.append(
                            ToolMessage(
                                content=result,
                                tool_call_id=response.tool_calls[i]['id']
                            )
                        )

                    final_response = self.llm_with_tools.invoke(self.messages)
                    self.messages.append(final_response)
                    return final_response.content

            self.messages.append(response)
            return response.content

        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        """대화 히스토리 초기화"""
        self.messages = [SystemMessage(content=SYSTEM_PROMPT)]

    async def arun(self, query: str) -> str:
        """
        Run agent asynchronously

        Args:
            query: User query

        Returns:
            Agent response
        """
        # For now, just call the sync version
        return self.run(query)


def create_agent(
    model_name: str = "gpt-4",
    temperature: float = 0.7,
    verbose: bool = True,
) -> CrewAgent:
    """
    Create an agent

    Args:
        model_name: OpenAI model name
        temperature: Temperature (0~1)
        verbose: Verbose output

    Returns:
        CrewAgent instance
    """
    return CrewAgent(
        model_name=model_name,
        temperature=temperature,
        verbose=verbose,
    )
