# app/models/schemas.py

from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str


class Recipe(BaseModel):
    id: int
    name: str
    time: Optional[int]
    reason: Optional[str]
    ingredients: List[str]


class NutritionInfo(BaseModel):
    id: int
    name: str
    protein: str
    carbs: str
    fat: str
    health_score: int


class FullResponse(BaseModel):
    recipes: List[Recipe]
    nutrition: List[NutritionInfo]


