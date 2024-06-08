from pprint import pprint

from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_aws import ChatBedrock
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate

db = SQLDatabase.from_uri("sqlite:///db/Chinook.db")
result = db.run("SELECT * FROM Artist LIMIT 12;", fetch="cursor")

print(type(result))
pprint(list(result.mappings()))

result = db.run("SELECT * FROM Artist LIMIT 12;", fetch="all")
print(type(result))
print(result)

result = db.run("SELECT * FROM Artist LIMIT 12;", fetch="one")
print(type(result))
print(result)

result = db.run(
    "SELECT * FROM Artist WHERE Name LIKE :search;",
    parameters={"search": "p%"},
    fetch="cursor",
)
pprint(list(result.mappings()))
print()

llm = ChatBedrock(
    region_name="us-west-2",
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    model_kwargs={
        "temperature": 1.0,
        "top_p": 1.0,
        "top_k": 255,
        "max_tokens": 4096,
    },
    streaming=True
)
chain = create_sql_query_chain(llm, db)
# response = chain.invoke({"question": "How many employees are there"})
# print(response)
# print()


print("# db.dialect")
print(db.dialect)
print()

print("# db.get_usable_table_names")
print(db.get_usable_table_names())
print()

print("# db.get_table_info")
print(db.get_table_info())
print()

system_message = """
    You are a {dialect} expert. 
    You are interacting with a user who is asking you questions about the company's database.
    Based on the database schema below, write a SQL query that would answer the user's question.

    Here is the database schema:
    <schema> {table_info} </schema>

    Write ONLY THE SQL QUERY and nothing else. 
    Do not wrap the SQL query in any other text, not even backticks.

    For example:
    Question: Name 10 customers
    SQL Query: SELECT Name FROM Customers LIMIT 10;

    Your turn:
    Question: {question}
    SQL Query:
    """

human_message = [{"type": "text", "text": "{question}"}]

template = [
    ("system", system_message),
    ("human", human_message),
]

prompt = ChatPromptTemplate.from_messages(template)
