"""
main.py — Hello LangChain
Minimal working example: load an LLM via Ollama and run a simple Q&A chain.
"""

import sys
import os

# Allow importing from the repo root's common/ package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from common.llm_factory import get_llm
from common.utils import get_logger

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logger = get_logger(__name__)


def main():
    logger.info("Initialising LLM...")
    llm = get_llm()

    prompt = PromptTemplate.from_template(
        "Answer the following question in 2-3 sentences.\n\nQuestion: {question}\n\nAnswer:"
    )

    chain = prompt | llm | StrOutputParser()

    question = "What is LangChain and why is it useful for building AI agents?"
    logger.info(f"Question: {question}")

    response = chain.invoke({"question": question})

    print("\n--- Response ---")
    print(response)
    print("----------------\n")


if __name__ == "__main__":
    main()
