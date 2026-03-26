
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

from src.agent_classes import *


load_dotenv()

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
            "You should tell if the player response is accepted or not, and that's it.",
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
    answer = verify_answer("Angelian Jolie", "Brad Pitt")
    print(answer)
    return

if __name__ == "__main__":
    main()
