import sys
import os
# Add current dir to path to import walmart_chat
sys.path.append(os.getcwd())
try:
    from walmart_chat import load_config, load_data_to_sqlite, discovery_step
    from langchain_community.utilities import SQLDatabase
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def verify():
    print("Verifying loading...")
    config = load_config()
    # Use config but override db for safety or reuse
    db_path = config['db_path']
    engine = load_data_to_sqlite(config['csv_path'], db_path)
    
    db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    print("Database connected.")
    
    discovery_step(db)
    print("\nVerification of data loading and discovery steps: SUCCESS")

if __name__ == "__main__":
    verify()
