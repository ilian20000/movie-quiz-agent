
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# from agent_classes import *
from src.agent_classes import *


load_dotenv()


def get_game_preferences(user_answer):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )
    
    template = ChatPromptTemplate.from_messages(
        [
            (
            "system",
            "You are the game master of the movie quiz game, you have to understand if the user requests a specific theme or movie genre. If he has specific needs, tell back only the requested genre, other wise say nothing",
            ),
            ("human", "{user_answer}"),
        ]
    )

    tmodel = template | model
    response = tmodel.invoke({
        "user_answer": user_answer
        })

    return response.content


def verify_answer(user_answer, expected_answer):
    model = ChatOpenAI(
        model=os.getenv("AI_MODEL"),
        base_url=os.getenv("AI_ENDPOINT"),
        api_key=os.getenv("AI_API_KEY"),
    )
    
    template = ChatPromptTemplate.from_messages(
        [
            (
            "system",
            "You are the referee of a quiz game, the expected answer is {expected_answer}. " \
            "If the user answer is included in the list or close enough or with a few letters of difference can be okay. " \
            "You should tell if the player response is accepted or not, and that's it. You shall NOT try to ask any other question or keep the game running." \
            "Occasionally you inform the user that the difficulty is ramping up only if he wins",
            ),
            ("human", "{user_answer}"),
        ]
    )

    structured_model = template | model.with_structured_output(AnswerValidation)
    response = structured_model.invoke({
        "user_answer": user_answer,
        "expected_answer": expected_answer
        })

    return response
    

def main():
    # answer = verify_answer("Angelian Jolie", "Brad Pitt")
    # print(answer)
    # answer = get_game_preferences("Pas de préférences")
    answer = get_game_preferences("Je veux de la science-fiction")
    print(answer)
    return

if __name__ == "__main__":
    main()
