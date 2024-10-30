from typing import Dict
from utils.score_interpreter import interpret_score
from langchain_ollama import OllamaLLM
import asyncio

model = OllamaLLM(model="llama3", temperature=0.7, num_ctx=2048)

async def generate_analysis(faction_name: str, stats: Dict[str, int]) -> str:
    """Generate a faction analysis based on given stats."""
    prompt = (
        f"Analyze the {faction_name} faction with these stats:\n"
        f"Tankiness: {interpret_score(stats['tankiness'], 'Tankiness')}\n"
        f"Melee: {interpret_score(stats['melee_strength'], 'Melee')}\n"
        f"Ranged: {interpret_score(stats['ranged_strength'], 'Ranged')}\n"
        "In multiplayer battles, focus on advice on how to best to use the faction and it's strengths and weaknesses. Be short and concise. "
    )
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, model.invoke, prompt)
        return str(response)[:1900]
    except Exception as e:
        return f"Error generating analysis: {e}"
