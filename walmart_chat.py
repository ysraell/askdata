import json
import pandas as pd
import sqlalchemy
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
try:
    from langchain.chains import create_sql_query_chain
except ImportError:
    try:
        from langchain_classic.chains import create_sql_query_chain
    except ImportError:
         print("Error: Could not import create_sql_query_chain from langchain or langchain_classic")
         sys.exit(1)

from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
import time
import os
import sys
from datetime import datetime

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found.")
        sys.exit(1)

def load_data_to_sqlite(csv_path, db_path):
    print(f"Loading data from {csv_path} to {db_path}...")
    try:
        df = pd.read_csv(csv_path)
        # Convert Date to datetime for better querying
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True) # Assuming DD-MM-YYYY format based on user description "12-Feb-10"
        
        engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
        df.to_sql('walmart_sales', engine, index=False, if_exists='replace')
        print("Data loaded successfully.")
        return engine
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

def discovery_step(db):
    print("\n--- Discovery Step ---")
    print("running queries to discover the metada about the data...")
    queries = {
        "tables": "SELECT name FROM sqlite_master WHERE type='table';",
        "schema": "PRAGMA table_info(walmart_sales);",
        "count": "SELECT COUNT(*) FROM walmart_sales;",
        "sample": "SELECT * FROM walmart_sales LIMIT 3;"
    }
    
    metadata_summary = ""
    for key, q in queries.items():
        try:
            result = db.run(q) 
            metadata_summary += f"\n--- {key.upper()} ---\n{result}\n"
            print(".", end="", flush=True)
            time.sleep(0.3)
        except Exception as e:
            print("x", end="", flush=True)
    
    print("\nDiscovery complete. Metadata assimilated.")
    return metadata_summary

def get_answering_utils(llm, db, discovery_metadata):
    # 1. Chain to find initial data
    find_data_prompt = PromptTemplate.from_template(
        """You are an expert data analyst. Based on the following metadata and the user question, 
        write a SQL query to 'find' relevant data that might be needed to answer the question. 
        This is an exploratory query (e.g., checking specific categories, date ranges, or sample rows).

        Metadata:
        {metadata}

        Question: {question}
        SQL Query: """
    )
    find_data_chain = find_data_prompt | llm | StrOutputParser()

    # 2. Chain to generate the final answer SQL
    final_sql_prompt = PromptTemplate.from_template(
        """You are an expert data analyst. Based on the metadata, the user question, 
        and the initial findings from a preliminary query, write the final SQL query 
        to answer the user question accurately.

        Metadata:
        {metadata}

        Initial Findings: {findings}

        Question: {question}
        Final SQL Query: """
    )
    final_sql_chain = final_sql_prompt | llm | StrOutputParser()

    # 3. Final synthesis
    synthesis_prompt = PromptTemplate.from_template(
        """Based on the user question and the results of the data analysis, provide a clear and concise answer.

        Question: {question}
        Data Analysis Results: {results}
        Answer: """
    )
    synthesis_chain = synthesis_prompt | llm | StrOutputParser()

    return find_data_chain, final_sql_chain, synthesis_chain

def main():
    config = load_config()
    os.environ["GOOGLE_API_KEY"] = config['google_api_key']
    load_data_to_sqlite(config['csv_path'], config['db_path'])
    db = SQLDatabase.from_uri(f"sqlite:///{config['db_path']}")
    llm = ChatGoogleGenerativeAI(model=config['model_name'], temperature=0)
    
    # Discovery Step (returns metadata)
    metadata = discovery_step(db)
    
    # Setup answering components
    find_data_chain, final_sql_chain, synthesis_chain = get_answering_utils(llm, db, metadata)
    
    print("\n--- Chat Simulation Started (Type 'exit' to quit) ---")
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            print("System: Answering step initiated...")
            
            # Sub-step 1: Finding the data
            print("System: Step 1 - Finding relevant data...", end="", flush=True)
            initial_query_raw = find_data_chain.invoke({"question": user_input, "metadata": metadata})
            # Clean up potential markdown from LLM
            initial_query = initial_query_raw.strip().replace("```sql", "").replace("```", "").strip()
            findings = db.run(initial_query)
            print(" Done.")
            
            # Sub-step 2: The query that will answer the question
            print("System: Step 2 - Generating final answer...", end="", flush=True)
            
            # Save Step 2 input data as requested
            step2_data = {
                "question": user_input,
                "metadata": metadata,
                "findings": findings
            }
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            filename = f"step2_input_data_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(step2_data, f, indent=4)
            
            final_sql_raw = final_sql_chain.invoke({
                "question": user_input, 
                "metadata": metadata, 
                "findings": findings
            })
            final_sql = final_sql_raw.strip().replace("```sql", "").replace("```", "").strip()
            results = db.run(final_sql)
            
            response = synthesis_chain.invoke({"question": user_input, "results": results})
            print(" Done.")
            
            print(f"\nBot: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
