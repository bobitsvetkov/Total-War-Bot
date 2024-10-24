import json
import logging
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'units_stats.json')

# Load unit data from JSON
with open(json_path) as f:
    unit_data = json.load(f)

model = OllamaLLM(model="llama3")

stats_template = (
    "You have access to a dataset of unit stats. When asked about a specific unit's stats or attributes, "
    "refer to the provided data. The relevant unit's information is as follows: {unit_data}. "
    "Provide an answer based on this information only."
)
def query_unit_stats(unit_name):
    """Extract specific stat information for a unit."""
    logging.info(f"Looking for unit: {unit_name}")
    for unit in unit_data:
        if unit['Unit'].lower() == unit_name.lower():
            return unit
    return "Unit not found"

def ask_ollama_question(unit_name, stat):
    """Use Ollama to generate a structured response based on user query."""
    unit_stats = query_unit_stats(unit_name, stat)
    logging.info(f"Unit Stats Retrieved: {unit_stats}")
    prompt_template = ChatPromptTemplate.from_template(stats_template)
    chain = prompt_template | model
    response = chain.invoke({"unit_data": unit_stats})
    return response


