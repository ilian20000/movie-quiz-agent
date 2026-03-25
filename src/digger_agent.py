"""
DICT QUERY PARAMETERS :
{
    difficulty: float, (min= 0, max= 1)
    preferences: str, (genres imdb, langage, etc...)
    game_mode: str, (type de questions posées : date, actors, director, etc)
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

"""Giving a list of options in the imdbapi format, return the response to the https call"""
def fetch_imdb_data(options : dict):
    url = "https://api.imdbapi.dev/titles"
    url += "?"
    for opt in options.keys():
        if isinstance(options[opt], list):
            if len(options[opt]) > 0:
                e = random.choice(options[opt])
                url += opt + "=" + e + "&"
        else:
            url += opt + "=" + options[opt] + "&"
    url += "&languageCodes=fr"
    url += "&sortBy=SORT_BY_USER_RATING_COUNT&sortOrder=DESC"
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

"""Take a response of an imdbapi https call
Return a pair with : 
- the full description of a film, taking into account the difficulty
- the new difficulty"""
def choose_artwork(data, difficulty):
    choice = random.choice(data["titles"])
    url = "https://api.imdbapi.dev/titles/" + choice["id"]
    print("API call to Imdb : ", url)
    response = requests.get(url)
    data = response.json()

    return data

def get_info(model, data, parameters):
    filtered_data = {
        "type" : data["type"],
        "title" : data["primaryTitle"],
        "year" : data["startYear"],
        "genres" : data["genres"],
        "plot" : data["plot"],
        "director" : [direct["displayName"] for direct in data["directors"]],
        #"writers" : [writ["displayName"] for writ in data["writers"]],
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
        0. If a game mode is specified then ask a question according to the game mode, and when the difficulty (0.0 to 1.0) is high give less details
        1. From 0.0 to 0.2 ask question about the name of the artwork, and give clues such as the name or the director, actors and the date.
        2. From 0.2 to 0.4 ask question about the director of the artwork, and give clues such as the name, actors and the date.
        3. From 0.4 to 0.6 ask question about the actors of the artwork, and give clues such as the name, director and the date.
        4. From 0.6 to 0.8 ask question about the date of the artwork, and give only the name of the artwork.
        5. From 0.8 to 1.0 ask question about the director of the artwork, and give only the plot of the artwork.
    4. THE ANSWER: Just the facts (name, year, or person).
    5. ANSWER Subject : Directors, Year, writters, actors
    """

    user_request = f"""
    CONTEXTE : {context}
    GAME_MODE : {parameters['game_mode']}
    DIFFICULTY : {parameters['difficulty']}

    Generate the question and the corresponding answer.
    """

    agent = create_agent(model, tools=[randomTool])

    messages_agent = [
        SystemMessage(content=GENERATOR_PROMPT),
        HumanMessage(content=user_request),
    ]

    response = agent.invoke({"messages": messages_agent})
    last_message = response["messages"][-1].content

    structured_gen = model.with_structured_output(GameQuestion)

    result = structured_gen.invoke(last_message)
        
    return result

def query_infos(parameters):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )

    structured_model = model.with_structured_output(Artworks_Informations)

    options = get_structured_api_options(structured_model, parameters["preferences"])

    data = fetch_imdb_data(options)
    artwork = choose_artwork(data)

    response = get_info(model, artwork, parameters)
    
    return response

def main():
    param = {
        "difficulty" : 0.0,
        "preferences" : "action movie",
        "game_mode" : ""
    }
    info = query_infos(param)

    print("Given info : ")
    print(info)

if __name__ == "__main__":
    main()
