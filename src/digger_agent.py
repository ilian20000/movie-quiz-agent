"""
DICT QUERY PARAMETERS :
{
    difficulty: float, (min= 0, max= 1)
    preferences: [str], (genres imdb, langage, etc...)
    game_mode: str, (pitch des règles actuelles du jeu)
}
"""

import json as j
import os
import requests
import random

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
from langchain_core.documents import Document
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from digger_agent_classes import *

load_dotenv()

def fetch_imdb_data(options : dict):
    url = "https://api.imdbapi.dev/titles"
    if(len(options) > 0):
        url += "?"
    for opt in options.keys():
        if isinstance(options[opt], list):
            if len(options[opt]) > 0:
                e = random.choice(options[opt])
                url += opt + "=" + e + "&"
        else:
            url += opt + "=" + options[opt] + "&"
    url += "&languageCodes=fr"
    print("API call to Imdb : ", url)
    response = requests.get(url)
    data = response.json()
    
    return data

def get_structured_api_options(model, prompt):
    messages = [
        HumanMessage(content=prompt),
    ]
    
    result1 = model.invoke(
        prompt
    )

    return result1.model_dump()

"""Take a response of an api call
Return the full description of a film"""
def choose_artwork(data):
    choice = random.choice(data["titles"])
    url = "https://api.imdbapi.dev/titles/" + choice["id"]
    print("API call to Imdb : ", url)
    response = requests.get(url)
    data = response.json()

    #url += "/akas"
    #for 

    return data

def get_info(model, data):
    filtered_data = {
        "type" : data["type"],
        "title" : data["primaryTitle"],
        "year" : data["startYear"],
        "genres" : data["genres"],
        "plot" : data["plot"],
        "director" : [direct["displayName"] for direct in data["directors"]],
        "writers" : [writ["displayName"] for writ in data["writers"]],
        "actors" : [star["displayName"] for star in data["stars"]],
        "originCountries" : data["originCountries"],
    }

    content = str(filtered_data)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=30)
    docs = [Document(page_content=x) for x in text_splitter.split_text(content)]

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
        api_key=os.getenv("AI_API_KEY"),
        base_url=os.getenv("AI_ENDPOINT")
    )
    vectorstore = DocArrayInMemorySearch.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()

    query = "Sum all the informations of the artwork?"
    relevant_docs = retriever.invoke(query)
    context = "\n".join([d.page_content for d in relevant_docs])

    GENERATOR_PROMPT = """
    You are a cinematic quiz bot. Your task is to generate a short question that contains clues.

    RULES:
    1. THE QUESTION: Must be short (max 20 words) but MUST include specific clues from the context (like actors or genre) so the user can actually guess.
    2. DIFFICULTY RULES:
        More the difficulty is low (0.0) give clues such as the name of the work, the year of the director
        More the difficulty is high (1.0) give clues such as the plot, the period, specific fact about the work
    4. THE ANSWER: Just the facts (name, year, or person).
    5. ANSWER Subject : Directors, Year, writters, actors
    """

    parameters = {"game_mode" : "work name",
                  "difficulty" : 0.0}

    user_request = f"""
    CONTEXTE : {context}
    GAME_MODE : {parameters['game_mode']}
    DIFFICULTY : {parameters['difficulty']}

    Generate the question and the corresponding answer.
    """

    messages_agent = [
        SystemMessage(content=GENERATOR_PROMPT),
        HumanMessage(content=user_request),
    ]

    structured_gen = model.with_structured_output(GameQuestion)

    result = structured_gen.invoke(messages_agent)
        
    return result

def query_infos(parameters):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )

    structured_model = model.with_structured_output(Artworks_Informations)

    prompt = """
    A animated movie
    """
    options = get_structured_api_options(structured_model, prompt)

    data = fetch_imdb_data(options)
    artwork = choose_artwork(data)

    response = get_info(model, artwork)

    return response

def main():
    param = {
        "difficulty" : 0.0,
        "preferences" : [],
        "game_mode" : "Find a info about the date of a film"
    }
    info = query_infos(param)

    print("Given info : ")
    print(info)

if __name__ == "__main__":
    main()
