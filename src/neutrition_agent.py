import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.state import chefState
from src.load_llm import get_llm
import json

def extract_features_node(state):
    recipes = state["ranked"]

    simplified = []

    for r in recipes:
        simplified.append({
            "id": r["id"],
            "name": r["name"],
            "ingredients": r.get("ingredients"),
            "time": r.get("time"),
            "reason": r.get("reason"),
        })

    return {**state,
        "processed_recipes": simplified
    }

def nutritionNode(state:chefState):
    recipes=state["processed_recipes"]
    NUTRITION_PROMPT = """
You are a nutrition expert.

Analyze each recipe based on ingredients.

Return STRICT JSON:
[
  {{ "id": "",
    "name": "",
    "protein": "low/medium/high",
    "carbs": "low/medium/high",
    "fat": "low/medium/high",
    "health_score": 1-10
  }}
]

Recipes:
{recipes}
"""
    prompt=NUTRITION_PROMPT.format(recipes=recipes)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")
    nutrition_info=json.loads(result)
    return {
        **state,
        "nutrition_info": nutrition_info
    }

def suggestNode(state:chefState):
    recipes=state["processed_recipes"]
    analysis=state["nutrition_info"]
    SUGGESTION_PROMPT = """
You are a nutrition coach.

For each recipe:
RETURN ONLY STRICT JSON:
[
{{
id: "",
name: "",
tips: [2-3 improvement tips to make the recipe healthier]
}},
]

Recipes:
{recipes}

Nutrition analysis:
{analysis}
"""
    prompt=SUGGESTION_PROMPT.format(recipes=recipes,analysis=analysis)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")
    suggestions=json.loads(result)
    return {
        **state,
        "suggestions": suggestions
    }


def formatInstructions(processed_recipes):
    ids=[r["id"] for r in processed_recipes]
    with open("data/recipes.json", 'r',encoding="utf-8") as file:
        data = json.load(file)
    
    instructions=[]
    for recipe in data:
        if recipe["id"] in ids:
            instructions.append({
                "id": recipe["id"],
                "instructions": recipe["instructions"]
            })

    instruction_prompt="""
You are a professional Indian chef.

Your task is to convert raw cooking instructions from {instructions} list into clean, step-by-step recipe instructions.

Input:
An array of unstructured or poorly written cooking steps.

Instructions:
- Rewrite each step clearly and professionally
- Make steps easy to follow for home cooking
- Use proper cooking terminology (e.g., sauté, simmer, mix)
- Ensure steps are in logical order
- Keep each step concise (1–2 lines max)
- Fix grammar and clarity
- Do NOT add new steps or ingredients
- Do NOT remove important actions

IMPORTANT:
- Merge duplicate or repeated steps
- Split overly long steps into smaller ones
- Ensure numbering/order is correct

Output format:
Return ONLY a JSON array of strings.
[
{{
"id": "",
"instructions": [ "Step 1", "Step 2", "Step 3" ]
}},
]

Example Output:
[ {{
  "id": "5",
  "instructions": ["Heat oil in a pan.",
  "Add cumin seeds and let them splutter.",
  "Add onions and sauté until golden brown."]

}},]

"""
    prompt=instruction_prompt.format(instructions=instructions)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")
    instructions=json.loads(result)
    return {
        "instructions": instructions
    }
