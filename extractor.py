import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# --- 1. Define your desired JSON output structure using Pydantic ---
class EntityRelation(BaseModel):
    subject: str = Field(description="The primary entity, e.g., 'APT29'")
    relationship: str = Field(
        description="The action or link, e.g., 'uses', 'targets', 'attributed_to'"
    )
    object: str = Field(
        description="The secondary entity, e.g., 'Triton Malware', 'CVE-2023-1234'"
    )


class CyberEntities(BaseModel):
    threat_actors: Optional[List[str]] = Field(
        description="All threat actor groups or individuals"
    )
    malware: Optional[List[str]] = Field(
        description="All malware, ransomware, or tools"
    )
    vulnerabilities: Optional[List[str]] = Field(
        description="All CVEs or named vulnerabilities"
    )
    indicators: Optional[List[str]] = Field(
        description="All IPs, domains, or file hashes"
    )
    attack_patterns: Optional[List[str]] = Field(
        description="All attack techniques, e.g., 'Phishing'"
    )
    relations: Optional[List[EntityRelation]] = Field(
        description="All identified relationships between entities"
    )


# --- 2. Set up the LLM, Parser, and Prompt ---
def get_extraction_chain():
    load_dotenv()
    # Set your API key
    gemini_key = os.getenv("OPENAI_API_KEY")

    # 2. Check if the variable actually has a value.
    if gemini_key:
        # 3. If it exists, assign it. The type checker now knows
        #    gemini_key is a string, not None.
        os.environ["OPENAI_API_KEY"] = gemini_key
    else:
        # 4. If it's None or empty, print an error and stop.
        print("ERROR: OPENAI_API_KEY not found in .env file.")
        print("Please ensure your .env file is correct.")
        return  # Stop the function

    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4")

    # Initialize the parser
    parser = PydanticOutputParser(pydantic_object=CyberEntities)

    # Create the prompt template
    prompt = PromptTemplate(
        template="""
        Analyze the following cybersecurity article. Extract all key entities and their relationships.
        {format_instructions}
        
        Article Text:
        "{article_text}"
        """,
        input_variables=["article_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create the chain
    chain = prompt | llm | parser
    return chain


def extract_entities(articles):
    """Uses the LLM chain to extract entities from a list of articles."""
    print("Initializing LLM chain for extraction...")
    chain = get_extraction_chain()
    all_extractions = []

    if chain is None:
        print("Chain initialization failed. Aborting extraction.")
        return []  # Return an empty list

    for i, article in enumerate(articles):
        print(f"Extracting from article {i + 1}/{len(articles)}: {article['title']}")
        try:
            # Run the extraction
            response = chain.invoke({"article_text": article["content"]})
            # Store the source URL with the extraction
            all_extractions.append(
                {"source_url": article["link"], "entities": response.dict()}
            )
        except Exception as e:
            print(f"Failed to extract from {article['link']}. Error: {e}")

    return all_extractions


if __name__ == "__main__":
    # Load the articles scraped in the previous step
    with open("articles.json", "r", encoding="utf-8") as f:
        articles_to_process = json.load(f)

    extractions = extract_entities(articles_to_process)

    # Save extractions to a new file
    with open("extractions.json", "w", encoding="utf-8") as f:
        json.dump(extractions, f, indent=2)

    print("Successfully extracted entities and saved to extractions.json")
