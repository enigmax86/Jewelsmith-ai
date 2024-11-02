import streamlit as st
from streamlit_chat import message
from timeit import default_timer as timer
from langchain_community.graphs import Neo4jGraph
from langchain.chains import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import dotenv
import os

# Load environment variables for credentials
dotenv.load_dotenv()

# LLM Configuration
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))

# Neo4j Configuration
neo4j_url = os.getenv("NEO4J_CONNECTION_URL")
neo4j_user = os.getenv("NEO4J_USER")
neo4j_password = os.getenv("NEO4J_PASSWORD")

# print(neo4j_url , neo4j_user , neo4j_password)

# Cypher generation prompt
cypher_generation_template = """
You are an expert Neo4j Cypher translator who converts English to Cypher based on the Neo4j Schema provided, following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE, HAVING keywords in the cypher. Use alias when using the WITH keyword
3. Use only Nodes and relationships mentioned in the schema
4. Always do a case-insensitive and fuzzy search for any properties related search. 
5. Never use relationships that are not mentioned in the given schema
6. Make sure there is no error in the cypher query in terms of syntax

schema: {schema}

Question: {question}
"""

# Define cypher and QA prompt templates
# cypher_generation_template = """
# (schema: {schema}, question: {question})...
# """
cypher_prompt = PromptTemplate(template=cypher_generation_template, input_variables=["schema", "question"])

# qa_prompt_template = """
# (context: {context}, question: {question})...
# """

CYPHER_QA_TEMPLATE = """You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.

The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.

Make the answer sound as a response to the question. Do not mention that you based the result on the given information.

If the provided information is empty, give the recommendations according to the provided context from your side.

Final answer should have 1 top recommendation and 2-3 other recommendations structed properly as a response from a chatbot and separated by new lines as a string. 
Information:
{context}

Question: {question}
Helpful Answer:"""

qa_prompt = PromptTemplate(template=CYPHER_QA_TEMPLATE , input_variables=["context", "question"])

def query_graph(user_input):
    graph = Neo4jGraph(url=neo4j_url, username=neo4j_user, password=neo4j_password)
    chain = GraphCypherQAChain.from_llm(
        llm=llm, graph=graph, cypher_prompt=cypher_prompt, qa_prompt=qa_prompt, verbose=True,
        return_intermediate_steps=True, allow_dangerous_requests=True
    )
    result = chain(user_input)
    return result

def generate_recommendations(basic_info):
    user_input = f"Recommend {basic_info['jewelry_type']} for a {basic_info['age_group']} year old {basic_info['gender']} for a {basic_info['occasion']}. Make sure to only include suggestions for this jewelryType : {basic_info['jewelry_type']} "
    result = query_graph(user_input)
    recommendations = result["result"]
    return recommendations

# Streamlit UI
# st.set_page_config(layout="wide")
# st.title("Jewelsmith AI - Customized Jewelry Recommendations")

# basic_info = {
#     "username": st.text_input("Username"),
#     "occasion": st.selectbox("Occasion", ["Engagement","Wedding", "Anniversary", "Birthday", "Daily-wear"]),
#     "purchase_type": st.radio("Gift or Personal Purchase", ["Gift", "Personal"]),
#     "gender": st.selectbox("Gender", ["Male", "Female", "Other"]),
#     "age_group": st.radio("Age Group", ["18-24", "25-30", "31-40", "41-50", "51+"]),
#     "religion": st.text_input("Religion (optional)"),
#     "jewelry_type": st.selectbox("Type of Jewelry", ["Rings", "Necklaces", "Pendants", "Bracelets", "Earrings"]),
#     "budget": st.radio("Budget", ["<10k INR", "10k-20k INR", "20k-50k INR", "50k INR or more"])
# }

# if st.button("Get Recommendations"):
#     with st.spinner("Finding the perfect jewelry for you..."):
#         recommendations = generate_recommendations(basic_info)
#         st.write("Here are some recommendations based on your preferences:")
#         st.write(recommendations)
