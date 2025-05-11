from dataclasses import dataclass
from pydantic_ai import Agent

agent = Agent(
        model='google-gla:gemini-1.5-flash-8b',
        system_prompt="Be concise, reply with one sentence."
)

result = agent.run_sync('Where does "hello world" come from?')
print(result.output)

