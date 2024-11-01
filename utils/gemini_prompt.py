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

def generate_analysis(faction_name: str, stats: Dict[str, float], all_factions_stats: Dict[str, Dict[str, float]]) -> str:
    """Generate a faction analysis based on given stats."""
    survivability_desc = interpret_score(stats['survivability'], "Survivability")
    melee_strength_desc = interpret_score(stats['melee_strength'], "Melee")
    ranged_strength_desc = interpret_score(stats['ranged_strength'], "Ranged")
    cavalry_prowess_desc = interpret_score(stats['cavalry_prowess'], "Cavalry Prowess")
    pilla_prowess_desc = interpret_score(stats['pilla_prowess'], "Pilla Prowess")
    all_factions_summary = "\n".join(
        [f"{faction} - Survivability: {data['survivability']}, Melee: {data['melee_strength']}, "
         f"Ranged: {data['ranged_strength']}, Cavalry: {data['cavalry_prowess']}, Pilla: {data['pilla_prowess']}"
         for faction, data in all_factions_stats.items()]
    )

    prompt = (
    f"Provide a detailed analysis of the {faction_name} faction in Rome 2 Total War Multiplayer Competitive Battles. "
    f"Consider the following key stats, each on a scale from 0 (weakest) to 100 (strongest), where lower values indicate weaknesses:\n"
    f"- **Survivability** ({stats['survivability']}): {survivability_desc} - Indicates the faction's durability (armor, health, morale).\n"
    f"- **Melee Strength** ({stats['melee_strength']}): {melee_strength_desc} - Reflects hand-to-hand combat capability.\n"
    f"- **Ranged Strength** ({stats['ranged_strength']}): {ranged_strength_desc} - Measures effectiveness with ranged units.\n"
    f"- **Cavalry Prowess** ({stats['cavalry_prowess']}): {cavalry_prowess_desc} - Assesses cavalry effectiveness in impact damage and overall combat effectiveness.\n"
    f"- **Pilla Prowess** ({stats['pilla_prowess']}): {pilla_prowess_desc} - Indicates efficiency of pilla-throwing units to disrupt enemy lines.\n\n"
    "Here are the stats for all factions:\n"
    f"{all_factions_summary}\n\n"
    "Based on these scores, provide a detailed analysis of strengths and weaknesses without contradictory claims."
    "Be short and concise"
)
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        content = response.text.strip()
        return content if content else "No analysis generated."
    except Exception as e:
        return f"Error generating analysis: {e}"

