import pandas as pd
import json
import re

def clean_ingredient(text):
    text = text.lower()

    # remove quantity + units
    text = re.sub(r'\d+\/?\d*\s*(cups|cup|tablespoons|tablespoon|teaspoons|teaspoon|tsp|tbsp|grams|g|kg)?', '', text)

    # remove brackets
    text = re.sub(r'\(.*?\)', '', text)

    # remove extra words
    text = text.replace("-", "").strip()

    return text

def filter_diet(df):
    print(df["Diet"].value_counts())

    not_to_select=['High Protein Non Vegetarian', 'Non Vegeterian', 'Eggetarian',]
    return df[~df['Diet'].isin(not_to_select)]
def process_ingredients(ingredient_text):
    items = ingredient_text.split(",")

    cleaned = []
    for item in items:
        c = clean_ingredient(item)
        if len(c) > 2:
            cleaned.append(c)

    return list(set(cleaned))


def clean_instructions(text):
    return text.replace("\n", " ").strip()


def csv_to_json(csv_file, output_file):
    df = pd.read_csv(csv_file)
    df=filter_diet(df)

    recipes = []

    for _, row in df.iterrows():

        recipe = {
            "id": int(row["Srno"]),
            "name": row["RecipeName"],
            "ingredients": process_ingredients(str(row["Ingredients"])),
            "instructions": clean_instructions(str(row["Instructions"])),

            "metadata": {
                "cuisine": row["Cuisine"],
                "course": row["Course"],
                "diet": row["Diet"],
                "prep_time": row["PrepTimeInMins"],
                "cook_time": row["CookTimeInMins"],
                "total_time": row["TotalTimeInMins"],
                "servings": row["Servings"]
            },

            "url": row["URL"],
            "embedding_text": f"""
{row["RecipeName"]}.
Cuisine: {row["Cuisine"]}.
Diet: {row["Diet"]}.
Ingredients: {process_ingredients(str(row["Ingredients"]))}.
"""
        }

        recipes.append(recipe)

    # save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(recipes)} recipes to {output_file}")


if __name__ == "__main__":
    csv_to_json("data/filtered_data.csv", "data/recipes.json")