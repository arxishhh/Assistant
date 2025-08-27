from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain import hub
from utils.tools import *


def get_tools(query):
    lower_query = query.lower()
    conversion_keywords = [
        "convert", "conversion", "exchange", "currency", "rate", "forex",
        "price in", "amount in", "how much is",
        "worth in"
    ]
    definition_keywords = [
        "define", "definition", "meaning", "what is", "explain",
        "describe", "in simple terms"
    ]
    conversion = any(keyw in lower_query for keyw in conversion_keywords)
    definition = any(keyw in lower_query for keyw in definition_keywords)
    tools = [context_retriever]
    if conversion and definition:
        branch = "Agent (multi-tool orchestration)"
        reasoning = "Mixed query detected"
        tools.extend([currency_conversion,finops_definition])
    elif conversion:
        branch = "currency_conversion"
        reasoning = "Currency conversion detected"
        tools.append(currency_conversion)
    elif definition:
        branch = "finops_definition"
        reasoning = "Finops definition detected"
        tools.append(finops_definition)
    else:
        branch = "context_required"
        reasoning = "Query requires context"
    log_decision("Branch Selection",reasoning,branch)
    return tools

def agent(query):
    prompt = hub.pull('hwchase17/react')
    tools = get_tools(query)
    agents = create_react_agent(
        llm=model,
        tools=tools,
        prompt=prompt
    )
    agents_executor = AgentExecutor(
        agent=agents,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )
    response = agents_executor.invoke({
                                         'input': query},
                                     return_intermediate_steps=True)
    return {
        'answer': response['output'],
        'intermediate_steps': response['intermediate_steps']
    }

if __name__ == '__main__':
    query = input("Enter query: ")
    print(agent(query))




