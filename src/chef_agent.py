import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.state import chefState
from langgraph.graph import StateGraph, END

import re
from src.load_llm import get_llm
from src.rag import create_vector_db , retriever
import json
from langchain_core.documents import Document
from src.neutrition_agent import nutritionNode, suggestNode, formatInstructions,extract_features_node

def parse_intent(chef_state: chefState):
    query = chef_state["query"].lower()

    PARSER_PROMPT = """
Extract structured constraints from user query.


Return JSON with:
- diet (Vegetarian / High Protein Vegetarian / Vegan)
- max_time 30 if quick, 60 if medium, 90 if long
- spice (low/medium/high)
- course (breakfast/lunch/dinner)
- goal (Diabetic Friendly / gluten free / suger free / sattvic / high protein) optional

Query: {query}
"""
    prompt = PARSER_PROMPT.format(query=query)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")

    return {
        **chef_state,
        "constraints": result
    }

def retrieve_node(state:chefState):
    query = state["query"]
    rv=retriever()
    docs = rv.invoke(query)

    recipes = []
    for doc in docs:
        recipe = doc.metadata

        recipes.append({
          "id":recipe["id"],"name":recipe["name"],
         "cuisine": recipe["cuisine"],
         "course": recipe["course"],"diet": recipe["diet"],
         "prep_time": recipe["prep_time"],"cook_time": recipe["cook_time"],
         "total_time": recipe["total_time"],"servings": recipe["servings"]
        })
    print(len(recipes))
    return {
        **state,
        "retreived": recipes
    }
def load_json(file_path):
    
    with open(file_path, 'r',encoding="utf-8") as file:
        data = json.load(file)
    
    documents=[]
    for recipe in data:
        content=recipe["embedding_text"]
        documents.append(Document(page_content=content,metadata={"id":recipe["id"],"name":recipe["name"],"cuisine": recipe["metadata"]["cuisine"],         "course": recipe["metadata"]["course"],"diet": recipe["metadata"]["diet"],"prep_time": recipe["metadata"]["prep_time"],"cook_time": recipe["metadata"]["cook_time"],"total_time": recipe["metadata"]["total_time"],"servings": recipe["metadata"]["servings"]}))
    return documents


def rankingNode(state:chefState):
    query=state["query"]
    recipes=state["filtered"]

    CHEF_PROMPT = """
You are a professional Indian chef.Reason like an Indian home chef giving practical advice.

Your job:
- Suggest the BEST 3 recipes from the given list
- DO NOT invent new recipes
- ONLY use provided recipes



User request:
{query}

Available recipes:
{recipes}

Instructions:
- Return ONLY JSON
- Include:
    id
    name
    time
    reason (why it fits user need)
    ingredients

Keep reasons short and practical.
FROMAT(RETURN JSON ONLY):-
[
{{"id": "",
"name": "",
"time": "",
"reason": "",
"ingredients": ""}}]
"""

    prompt=CHEF_PROMPT.format(query=query,recipes=recipes)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")
    ranked_recipes=json.loads(result)
    return {
        **state,
        "ranked": ranked_recipes
    }

def filterNode(state:chefState):
    print(state)
    
    retrieved=state["retreived"]
    constraints=state["constraints"]

    FILTER_PROMPT="""
    Filter retrieved nodes  based on constraints and retrieve data and give top 10 recipes.

    Constraints: {constraints}
    Retrieved Nodes: {retrieved}

    return strict JSON only :
    [
        {{
            "id": "",
            "name": "",
            "cuisine": "",
            "course": "",
            "diet": "",
            "prep_time": "",
            "cook_time": "",
            "total_time": "",
            "servings": ""
        }},
    ]

    """
    prompt=FILTER_PROMPT.format(constraints=constraints,retrieved=retrieved)
    result=get_llm(prompt)
    result=result.strip("```json").strip("```")
    result=json.loads(result)
    return {
        **state,
        "filtered": result
    }


def save_initial():
    import json

    data = [
    {
        "query": "i want quick vegetarian dish"
    }
    ]

# Save with UTF-8 (ensure_ascii=False preserves special chars)
    with open("data/queries.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def extract_recipe(result):

    processed_recipes=result["processed_recipes"]
    tips=result["suggestions"]
    return {
        "recipes": processed_recipes,
        "tips": tips
    }
def pipeline(query:str):
    graph=StateGraph(chefState)
    graph.add_node("parse_intent",parse_intent)
    graph.add_node("retrieve",retrieve_node)
    graph.add_node("filter",filterNode)
    graph.add_node("ranking",rankingNode)
    graph.add_node("extract_features",extract_features_node)
    graph.add_node("nutrition_analysis",nutritionNode)
    graph.add_node("suggestions",suggestNode)

    graph.set_entry_point("parse_intent")

    graph.add_edge("parse_intent","retrieve")
    graph.add_edge("retrieve","filter")
    graph.add_edge("filter","ranking")
    graph.add_edge("ranking","extract_features")
    graph.add_edge("extract_features","nutrition_analysis")
    graph.add_edge("nutrition_analysis","suggestions")
    graph.add_edge("suggestions",END)

    app=graph.compile()
    initial_state = chefState(query=query)
    result=app.invoke(initial_state)
    instructions=formatInstructions(result["processed_recipes"])
    return result,instructions

def main():
    save_initial()
    graph=StateGraph(chefState)
    graph.add_node("parse_intent",parse_intent)
    graph.add_node("retrieve",retrieve_node)
    graph.add_node("filter",filterNode)
    graph.add_node("ranking",rankingNode)
    graph.add_node("extract_features",extract_features_node)
    graph.add_node("nutrition_analysis",nutritionNode)
    graph.add_node("suggestions",suggestNode)

    graph.set_entry_point("parse_intent")

    graph.add_edge("parse_intent","retrieve")
    graph.add_edge("retrieve","filter")
    graph.add_edge("filter","ranking")
    graph.add_edge("ranking","extract_features")
    graph.add_edge("extract_features","nutrition_analysis")
    graph.add_edge("nutrition_analysis","suggestions")
    graph.add_edge("suggestions",END)

    app=graph.compile()
    initial_state = chefState(
        query="I want a quick vegetarian dinner recipe that is high protein",
    )
    result=app.invoke(initial_state)
    instructions=formatInstructions(result["processed_recipes"])

if __name__ == "__main__":    main()