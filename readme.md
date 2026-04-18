# 🍳 AI Recipe + Nutrition Recommendation System

An end-to-end **AI-powered backend system** that recommends Indian recipes based on user constraints and provides intelligent nutrition insights using **RAG (Retrieval-Augmented Generation)** and **multi-agent architecture**.

---

## 🚀 Features

* 🔍 **Smart Recipe Retrieval (RAG)**

  * Uses vector search (FAISS/Chroma) over curated Indian recipes dataset
* 🧠 **Chef Agent**

  * Understands user intent (e.g., *“high protein veg dinner under 30 min”*)
  * Filters + ranks recipes based on constraints
* 🥗 **Nutrition Agent**

  * Analyzes recipes for protein, carbs, fat, and health score
  * Suggests improvements like a nutritionist
* ⚡ **FastAPI Backend**

  * High-performance API for real-time inference
* 🧵 **Background Processing**

  * Image scraping handled asynchronously
* 📦 **Modular Architecture**

  * Clean separation between agents, pipeline, and API

---

## 🧠 System Architecture

```
User Query
   ↓
Parse Input
   ↓
RAG Retrieval (Vector DB)
   ↓
Filter + Ranking
   ↓
Chef Agent (LLM)
   ↓
Nutrition Agent (LLM)
   ↓
Final Structured Response (JSON)
```

---

## 🏗️ Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI app
│   ├── schema.py           # Pydantic models
│
├── src/
│   ├── chef_agent.py       # Chef agent (LangGraph)
│   ├── nutrition_agent.py  # Nutrition agent
│   ├── rag.py              # Vector DB logic
│   ├── load_llm.py         # Local LLM logic
│   ├── state.py            # agent states
│   ├── preprocess_data.py  # data preprocessing logic
│
├── data/
│   ├── recipes.json
│   ├── history.json
│   ├── queries.json
|   ├── images.json
│
├── images/                 # Downloaded recipe images
├── vector_db/              # Persisted embeddings
├── scrapper.py             # Image scraping logic
```

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **LLM:** Local LLM (via Ollama / LLaMA)
* **RAG:** Chroma / FAISS
* **Embeddings:** Sentence Transformers
* **Agents:** LangGraph
* **Async Tasks:** FastAPI BackgroundTasks

---

## 🧪 API Usage

### 🔹 POST `/recommend`

Generate recipe recommendations.

#### Request (Form Data)

```
query=high protein veg dinner under 30 minutes
```

#### Response (JSON)

```json
{
  "result": {
    "recipes": [
      {
        "id": 1,
        "name": "Paneer Bhurji",
        "time": 20,
        "reason": "High protein and quick to cook",
        "ingredients": ["paneer", "onion", "spices"]
      }
    ],
    "tips": "Use less oil and add vegetables for fiber"
  },
  "instructions": [
    ["Heat oil", "Add onions", "Cook paneer"]
  ]
}
```

---

### 🔹 GET `/delete_history`

Clears stored history and cached queries.

---

## 🧠 Agents Breakdown

### 👨‍🍳 Chef Agent

* Parses user constraints
* Retrieves relevant recipes using RAG
* Filters + ranks based on:

  * time
  * diet
  * ingredients
* Generates structured recipe suggestions

---

### 🥗 Nutrition Agent

* Analyzes ingredients using LLM
* Estimates:

  * protein
  * carbs
  * fat
  * health score
* Provides improvement tips

---

## ⚡ Performance Optimizations

* ✅ In-memory query caching
* ✅ Background image scraping
* ✅ Precomputed vector database
* ✅ Minimal LLM calls (only where needed)

---

## 🚀 Getting Started

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-recipe-system.git
cd ai-recipe-system
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Start FastAPI Server

```bash
uvicorn app.main:app --reload
```

---

### 5. Test API

Use:

* Postman
* curl
* or any frontend

---

## 🔮 Future Improvements

* 🔥 Replace BackgroundTasks with Celery + Redis
* 📊 Add real nutrition database (USDA / Indian DB)
* 🧠 Personalization (user preferences + memory)
* ⚡ Streaming responses (real-time LLM output)
* 🌐 Deploy with Docker + CI/CD

---

## 💡 Key Insights

* LLM is used only for reasoning, not raw retrieval
* RAG ensures factual consistency
* Multi-agent design separates concerns cleanly

---

## 🏆 Why This Project Matters

Most recipe apps:

* overload users with options
* lack personalization

This system:

* understands user intent
* reduces decision fatigue
* combines **AI + domain knowledge**

---

## 📜 License

MIT License

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

---

## ⭐ Support

If you find this useful, consider giving it a ⭐ on GitHub!
