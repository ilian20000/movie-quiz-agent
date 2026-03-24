import random

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum
import sys
class RandomInput(BaseModel):
    """Input for random choice in a list of string"""

    strList : List[str] = Field(description="The list of string where a random choice has to be performed")

@tool(args_schema=RandomInput)
def randomTool(strList: List[str]) -> str:
    """Perform a random choice in a list of string"""

    
    return random.choice(strList)

class GameQuestion(BaseModel):
    enigma: str = Field(description="The question")
    answer: str = Field(description="The correct answer expected (title of the film or precise information)")

class Artworks_Informations(BaseModel):
    """General Informations about a bunch of artwork"""

    types : List[Literal[ "MOVIE", "TV_SERIES", "TV_MINI_SERIES", "TV_SPECIAL", "TV_MOVIE", "SHORT", "VIDEO", "VIDEO_GAME"]] = Field(description="The list of artworks types, empty if none are specified")
    genres : List[Literal[ "Action", "Adventure", "Animation", "Biography", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "Film-Noir", "Game-Show", "History", "Horror", "Music", "Musical", "Mystery", "News", "Reality-TV", "Romance", "Sci-Fi", "Short", "Sport", "Talk-Show", "Thriller", "War", "Western" ]] = Field(description="The list of artworks genres, empty if none are specified")
    #countryCodes : List[str] = Field(description="The ISO 3166-1 code of countries artworks came from, empty if none are specified, perform a random choice when there is a list of country")
    #languageCodes : str = Field(description="The ISO 639-1 or ISO 639-2 code of countries artworks came from, put only one in the list if there is the choici between several, empty if none are specified")
    startYear: str = Field(description="The lower limit for artworks creation year, put 1800 if there is no upper limit")
    endYear: str = Field(description="The upper limit for artworks creation year, put 2100 if there is no upper limit")