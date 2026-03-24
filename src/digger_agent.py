
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
from digger_agent_classes import *

"""
DICT QUERY PARAMETERS :
{
    difficulty: float, (min= 0, max= 1)
    preferences: [str], (genres imdb, langage, etc...)
    game_mode: str, (pitch des règles actuelles du jeu)
}
"""




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
    messages = [
        SystemMessage("""You have to sum up all the informations contains in the following
                        dictionnary, which contains all the informations on a given artwork
                      Focus on factual informations, such as directors, main actors, year, plot, name.
                      """),
        HumanMessage(content=str(data)),
    ]
    temp_response = model.invoke(messages)
    print(temp_response.content)

    messages = [
        SystemMessage("""Ask a unique random question about the following description of an artwork
                      , Focus on factual informations, such as directors, main actors, year, plot, name"""),
        HumanMessage(content=temp_response.content),
    ]

    agent = create_agent(
        model,
        tools=[randomTool],
    )

    final_response = agent.invoke({"messages": messages})
    print(final_response["messages"][-1].content)



def query_infos(parameters):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )

    structured_model = model.with_structured_output(Artworks_Informations)

    prompt = """
    Un film de science fiction
    """
    options = get_structured_api_options(structured_model, prompt)

    data = fetch_imdb_data(options)
    artwork = choose_artwork(data)
    print(artwork)

    response = get_info(model, artwork)

    return response

def main():
    param = {
        "difficulty" : 0.0,
        "preferences" : [],
        "game_mode" : "Find a info about the date of a film"
    }
    query_infos(param)


if __name__ == "__main__":
    main()


    


# class MovieInput(BaseModel):
#     """Input for calculator."""
#     expression: str = Field(description="The parameters to ask for a movie")

# @tool(args_schema=MovieInput)
# def movie_query(expression: str) -> str:
#     """Get informations about a movie following the input criterias"""
#     movies = [ 
#         {
#         "name": "Inception",
#         "genre": "Sci-Fi",
#         "synopsis": "Un voleur qui s'approprie des secrets d'entreprise à l'aide d'une technique de partage de rêves se voit contraint d'effectuer la tâche inverse : implanter une idée dans l'esprit d'un PDG, pour revoir ses enfants."
#     },
#         {
#         "name": "LaLaLand",
#         "genre": "Comédie musicale",
#         "synopsis": "Tout en naviguant dans leurs carrières à Los Angeles, un pianiste et une actrice tombent amoureux tout en essayant de concilier leurs aspirations pour l'avenir."
#     },
#         {
#         "name": "Django Unchained",
#         "genre": "Comédie",
#         "synopsis": "Avec l'aide d'un chasseur de primes allemand, un esclave affranchi tente de sauver sa femme du violent propriétaire d'une plantation du Mississippi."
#     }
#     #     {
#     #     "name": "",
#     #     "genre": "",
#     #     "synopsis": ""
#     # },
#     ]

#     index_movie = random.randint(len(movies))
#     return movies[index_movie]["synopsis"]

    
# def main():
#     load_dotenv()
#     temp = 2
#     model = ChatOpenAI(
#         model=os.getenv("AI_MODEL"),
#         base_url=os.getenv("AI_ENDPOINT"),
#         api_key=os.getenv("AI_API_KEY"),
#         temperature= temp
# )

#     structured_model = model.with_structured_output(Artworks_Informations)

#     prompt = """
#     Un film de science fiction
#     """
#     options = get_structured_api_options(structured_model, prompt)

#     data = fetch_imdb_data(options)
#     artwork = choose_artwork(data)
#     print(artwork)

#     response = get_info(model, artwork)

#     return response

# def main():
#     param = {
#         "difficulty" : 0.0,
#         "preferences" : [],
#         "game_mode" : "Find a info about the date of a film"
#     }
#     query_infos(param)


# if __name__ == "__main__":
#     main()


#     # Examples of code → comment pairs
#     examples = [
#         {
#             "code": "total = sum(numbers)",
#             "comment": "# Calculates the sum of all numbers in the list",
#         },
#         {
#             "code": "users = [u for u in data if u.active]",
#             "comment": "# Filters the data list to only include active users",
#         },
#         {
#             "code": "db.save(record)",
#             "comment": "# Saves the record to the database",
#         },
#     ]

#     example_template = ChatPromptTemplate.from_messages(
#         [
#             ("human", "Code: {code}"),
#             ("ai", "{comment}"),
#         ]
#     )

#     few_shot_template = FewShotChatMessagePromptTemplate(
#         example_prompt=example_template,
#         examples=examples,
#     )

#     final_template = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 "Generate clear, concise comments for code based on these examples:",
#             ),
#             few_shot_template,
#             ("human", "Code: {code}"),
#         ]
#     )
#     agent = create_agent(model, tools=[movie_query])

#     query = "Give me a funny movie synopsis"

#     response = agent.invoke({"messages": [HumanMessage(content=query)]})
#     last_message = response["messages"][-1]
#     print(f" Agent: {last_message.content}\n")

# if __name__ == "__main__":
#     main()
