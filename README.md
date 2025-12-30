# Walmart Chat Bot (POC)

A Python-based chat interface that answers questions about the Walmart Sales dataset using Google Gemini and LangChain.

## How it Works "Under the Hood"

The system follows a structured pipeline to ensure accurate data extraction and answering:

### 1. Data Ingestion
- Loads `Walmart.csv` into a local SQLite database (`walmart.db`).
- Converts dates and ensures types are correct for SQL querying.

### 2. Discovery Step (The "Assimilation" Phase)
Before any interaction, the script performs a "Discovery" phase:
- It runs metadata queries (`TABLES`, `SCHEMA`, `COUNT`, `SAMPLE`) to understand the database structure.
- The results are stored in a **Discovery Summary**. This summary is passed as context to the LLM for every user question, so it knows the column names (e.g., `Weekly_Sales`, `Holiday_Flag`) without guessing.

### 3. Two-Step Answering Process
When you ask a question, the agent performs two distinct sub-steps:
- **Step 1: Finding Relevant Data**: The LLM uses the metadata to generate an exploratory SQL query. This query locates the specific rows or statistics needed.
- **Step 2: Generating Final Answer**: The results from Step 1 are combined with the original metadata to generate the final, precise SQL query and natural language response.

### 4. Logging & Debugging
- All inputs for **Step 2** (the most complex part) are logged into a timestamped JSON file (e.g., `step2_input_data_YYYYMMDD_HHMM.json`) for audit and debugging purposes.

---

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- A Google API Key from [Google AI Studio](https://aistudio.google.com/).

### 2. Configuration
Edit `config.json` in the project root:
```json
{
    "google_api_key": "YOUR_API_KEY",
    "model_name": "gemini-2.5-pro",
    "csv_path": "Walmart.csv",
    "db_path": "walmart.db"
}
```

### 3. Installation
Activate the provided virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Usage
Run the main script:
```bash
python walmart_chat.py
```

- Type your question when prompted (e.g., "What was the total sale for store 1 on holiday weeks?").
- Type `exit` to quit.

---

## Important Notes on Quotas
The multi-step reasoning makes several API calls per question. If you are on the **Gemini Free Tier**, you may hit rate limits (Error 429).
- **Tip**: Wait 60 seconds or switch to a lighter model like `gemini-2.0-flash-lite` in `config.json`.
