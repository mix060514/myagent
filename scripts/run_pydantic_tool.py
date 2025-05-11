from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

@dataclass
class DatabaseConn:
    @classmethod
    async def customer_name(cls, *, id: int) -> str | None:
        if id == 123:
            return 'John'
    
    @classmethod
    async def customer_balance(cls, *, id: int, include_pending: bool) -> float | None:
        if id == 123 and include_pending:
            return 123.45
        else:
            raise ValueError('Customer not found')

@dataclass
class SupportDependencies:
    customer_id: int
    db: DatabaseConn

@dataclass
class SupportOutput:
    support_advice: str = Field(description='Advice returned to the customer')
    block_card: bool = Field(description='Whether to block the customer\'s card')
    risk: int = Field(description='Risk level of query', ge=0, le=10)

support_agent = Agent(
        model='google-gla:gemini-1.5-flash-8b',
        deps_type=SupportDependencies,
        output_type=SupportOutput,
        system_prompt="You are a support agent in our bank, give the "
            "customer support and judge the risk level of their query."
)

@support_agent.system_prompt
async def add_customer_name(ctx: RunContext[SupportDependencies]) -> str:
    customer_name = await ctx.deps.db.customer_name(id=ctx.deps.customer_id)
    return f"Customer name is {customer_name!r}."


@support_agent.tool
async def customer_balance(ctx: RunContext[SupportDependencies], include_pending: bool) -> float | None:
    # print(f"{ctx.deps.customer_id=}, {include_pending=}")
    return await ctx.deps.db.customer_balance(
        id=ctx.deps.customer_id,
        include_pending=include_pending
    )
    
async def main():
    deps = SupportDependencies(customer_id=123, db=DatabaseConn())
    result = await support_agent.run('What is my balance? include pending =True', deps=deps)
    print(result.output)
    
    
    result = await support_agent.run('I just lost my card!', deps=deps)
    print(result.output)
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
