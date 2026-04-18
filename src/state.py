from typing import TypedDict,List,Dict

class chefState(TypedDict):
    query:str
    constraints:Dict
    retreived:List[Dict]
    filtered:List[Dict]
    response:str
    ranked:List[Dict]
    processed_recipes:List[Dict]
    nutrition_info:List[Dict]
    suggestions:List[Dict]
    instructions:List[Dict]
