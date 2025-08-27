from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import requests
import os
from pathlib import Path
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.log import *
from langchain_community.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

load_dotenv()
from langchain_chroma import Chroma
model = ChatGroq(model = os.getenv("OPEN_AI_MODEL"))
EXCHANGE_RATE_API = os.getenv('EXCHANGE_RATE_API')
parser = StrOutputParser()

@tool
def context_retriever(query : str) -> list:
    """Retrieve relevant contexts based on a query.
    Returns:
        list: A list of relevant contexts.
    """
    log_decision(step = "tool_selection",
    reasoning = "Query requires knowledge retrieval, using context_retriever",
    tool_used = "context_retriever"
    )
    try:
        vector_store = Chroma(collection_name='FinOps', persist_directory=str(Path(__file__).resolve().parent.parent/'database'),
                              embedding_function=embeddings)
        retriever = vector_store.as_retriever(search_kwargs={'k': 3})
        results =  retriever.invoke(query)
        log_decision(step = "context_retrieved",
                     reasoning = f"Retrieved {len(results)} relevant documents from knowledge base",
                     tool_used = "context_retriever")
        return results
    except Exception as e:
        error_msg = f"Context Retrieval failed: {str(e)}"
        log_decision(step = "retrieval_error",
                     reasoning = error_msg,
                     tool_used= "context_retriever")
        return [f"Error retrieving context: {str(e)}"]


@tool
def currency_conversion(conversion_string : str) -> str:
    """Perform currency conversion based on current exchange rates.
        Use this for queries containing 'convert', 'exchange', 'currency', etc.
        Args:
            conversion_string: Format: "amount,source_currency,target_currency" (e.g., "500.00,INR,USD")
        Returns:
            str: The converted amount with details
        """
    log_decision(
        step="tool_selection",
        reasoning="Query involves currency conversion, using currency_conversion tool",
        tool_used="currency_conversion",
    )

    try:
        parts = conversion_string.split(',')

        amount = float(parts[0].strip())
        source = parts[1].strip().upper()
        target = parts[2].strip().upper()

        log_decision(
            step="currency_api_call",
            reasoning=f"Converting {amount} {source} to {target}",
            tool_used="currency_conversion"
        )

        response = requests.get(
            f'https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API}/pair/{source}/{target}'
        )

        if response.status_code == 200:
            rate = response.json()['conversion_rate']
            converted_amount = amount * rate

            result = f"{amount} {source} = {converted_amount:.2f} {target} (Rate: {rate})"
            log_decision(
                step="conversion_success",
                reasoning=f"Successfully converted currency: {result}",
                tool_used="currency_conversion"
            )
            return result
        else:
            error_msg = f"API error: {response.status_code}"
            log_decision(
                step="api_error",
                reasoning=error_msg,
                tool_used="currency_conversion"
            )
            return error_msg

    except Exception as e:
        error_msg = f"Currency conversion error: {str(e)}"
        log_decision(
            step="conversion_error",
            reasoning=error_msg,
            tool_used="currency_conversion"
        )
        return error_msg


@tool
def finops_definition(word : str) -> str:
    """Generate a definition of a finops keyword in a precise and easy-to-understand format for beginners.
    Returns:
        str: A definition of the finops keyword in a beginner-friendly format.
    """
    log_decision(
        step="tool_selection",
        reasoning="Query requests definition, using finops_definition tool",
        tool_used="finops_definition",
    )
    try:
        prompt = PromptTemplate(
            template="""
                Define the given FinOps keyword in a clear, precise, and beginner-friendly way. Keep the explanation short and easy to understand.
                _______
                Keyword
                {word}
                """,
            input_variables=['word']
        )
        chain = prompt | model | parser
        definition = chain.invoke({'word': word})
        log_decision(
            step = "keyword_defined",
            reasoning = f"Successfully defined: {word}",
            tool_used="finops_definition"
        )
        return definition
    except Exception as e:
        error_msg = f"Finops definition error: {str(e)}"
        log_decision(
            step = "definiton_error",
            reasoning=error_msg,
            tool_used="finops_definition"
        )
        return error_msg

