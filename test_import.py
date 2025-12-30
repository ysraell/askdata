try:
    from langchain_classic.chains import create_sql_query_chain
    print("Found in langchain_classic.chains")
except ImportError:
    print("Not found in langchain_classic.chains")

try:
    from langchain_classic.chains.sql_database.query import create_sql_query_chain
    print("Found in langchain_classic.chains.sql_database.query")
except ImportError:
    print("Not found in langchain_classic.chains.sql_database.query")
