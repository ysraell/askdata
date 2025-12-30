import sys
try:
    import langchain
    print(f"Langchain version: {langchain.__version__}")
    print(f"Langchain path: {langchain.__path__}")
except ImportError:
    print("Langchain not found")

try:
    from langchain import chains
    print("langchain.chains imported")
    print(dir(chains))
except ImportError as e:
    print(f"Could not import langchain.chains: {e}")

try:
    from langchain.chains import create_sql_query_chain
    print("Found create_sql_query_chain in langchain.chains")
except ImportError:
    print("Not found in langchain.chains")

# Check community
try:
    from langchain_community.utilities import SQLDatabase
    print("SQLDatabase found in community")
except ImportError:
    print("SQLDatabase not found")
