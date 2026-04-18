import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import os
from src.chef_agent import pipeline
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.schema import QueryRequest,Recipe,NutritionInfo,FullResponse
from fastapi import FastAPI
import json
from scrapper import download_images,save_image
from fastapi import BackgroundTasks,Form

async def full_pipeline(query):
    result,instructions = pipeline(query)
    await extract_url(result)
    return extract_recipe(result),instructions

async def extract_url(result):
    print("extracting url")
    recipes=result["processed_recipes"]
    ids=[r["id"] for r in recipes]
    with open("data/recipes.json", 'r',encoding="utf-8") as file:
        data = json.load(file)
    
    for r in data:
        if r["id"] in ids:
            await download_images(r["url"],r["id"])
            file_path=f"images/{r['id']}.jpg"
            await save_image(file_path)
            append_data({"id": r["id"],"url": file_path},"data/images.json")



def extract_recipe(result):

    processed_recipes=result["processed_recipes"]
    tips=result["suggestions"]
    return {
        "recipes": processed_recipes,
        "tips": tips
    }
    

def append_data(data,file_path="data/history.json"):
    with open(file_path, 'r',encoding="utf-8") as file:
        existing_data = json.load(file)
        if len(existing_data) == 0:
            existing_data = []
    with open(file_path, 'w',encoding="utf-8") as file:
        existing_data.append(data)
        json.dump(existing_data, file, indent=4)

def check_query(query):
    with open("data/queries.json", 'r',encoding="utf-8") as file:
        data = json.load(file)
    i=-1
    for q in data:
        i+=1
        if q["query"] == query:
            return True,i
    return False,-1
app = FastAPI()
router = APIRouter()
app.include_router(router)
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return {
        "message": "Hello World"
    }
@app.post("/recommend")
async def recommend(bg_task: BackgroundTasks,data: str = Form(...)):
    check,index=check_query(data)
    if check:
        with open("data/history.json", 'r',encoding="utf-8") as file:
            dt = json.load(file)[index]
        return JSONResponse(content=dt)
    recipe,instructions = await full_pipeline(data)

    datas= {"result": recipe, "instructions": instructions}
    append_data(datas)
    append_data({"query": data},"data/queries.json")
    return JSONResponse(content=datas)
    

@app.get("/delete_history")
async def delete_history():
    with open("data/history.json", 'w',encoding="utf-8") as file:
        json.dump([], file, indent=4)
    with open("data/queries.json", 'w',encoding="utf-8") as file:
        json.dump([], file, indent=4)
    with open("data/images.json", 'w',encoding="utf-8") as file:
        json.dump([], file, indent=4)
    image_dir="images"
    for file in os.listdir(image_dir):
        if file.endswith(".png"):
            os.remove(os.path.join(image_dir, file))
    return JSONResponse(content={"message": "History deleted"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)