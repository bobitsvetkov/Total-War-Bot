from typing import Dict
from utils.score_interpreter import interpret_score
import os
from dotenv import load_dotenv
import google.generativeai as genai # type: ignore

load_dotenv("secret.env")
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API Key for Google Gemini is not found!")
genai.configure(api_key=api_key)

def generate_analysis(faction_name: str, stats: Dict[str, float]) -> str:
    """Generate a faction analysis based on given stats."""
    survivability_desc = interpret_score(stats['survivability'], "Survivability")
    melee_strength_desc = interpret_score(stats['melee_strength'], "Melee")
    ranged_strength_desc = interpret_score(stats['ranged_strength'], "Ranged")

    prompt = (
        f"Analyze the strength of the {faction_name} faction in Rome 2 Total War Multiplayer Competitive Battles "
        f"using the following stats:\n"
        f"- Survivability: {stats['survivability']} ({survivability_desc})\n"
        f"- Melee Strength: {stats['melee_strength']} ({melee_strength_desc})\n"
        f"- Ranged Strength: {stats['ranged_strength']} ({ranged_strength_desc})\n"
        "These stats are on a scale of 0 to 100, where 100 is the strongest. "
        "Do not assume any values below or beyond these. Provide concise advice on utilizing this faction’s strengths and weaknesses effectively."
    )
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        content = response.text.strip()
        return content if content else "No analysis generated."
    except Exception as e:
        return f"Error generating analysis: {e}"

