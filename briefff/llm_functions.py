from config import *
from openai import OpenAI
from octoai.client import Client
import random
from typing import List


def gpt4GenerateText(query):
    user = random.choice(list(GPT_API_KEYS.keys()))
    print(f"script key : {user}")
    gptClient = OpenAI(api_key=GPT_API_KEYS[user])
    #print(f"script key being used: {gptClient}")
    model_4 = "gpt-4-1106-preview"
    model_3 = "gpt-3.5-turbo-1106"

    completion = gptClient.chat.completions.create(
        model=model_4, messages=[{"role": "user", "content": query}]
    )
    return completion.choices[0].message.content


def gpt3GenerateText(query):
    gptClient = OpenAI(api_key=GPT_API_KEYS[random.choice(list(GPT_API_KEYS.keys()))])

    model_3 = "gpt-3.5-turbo-1106"
    completion = gptClient.chat.completions.create(
        model=model_3, messages=[{"role": "user", "content": query}]
    )
    return completion.choices[0].message.content

def mixtralGenerateText(query, maxtokens):
    octo_key = random.choice(list(OCTO_KEYS.keys()))
    print(f"now using octo key {octo_key}")

    octoClient = Client(OCTO_KEYS[octo_key])

    completion = octoClient.chat.completions.create(
        messages=[{"role": "user", "content": query}],
        model="mixtral-8x7b-instruct-fp16",
        max_tokens=maxtokens,
        presence_penalty=0,
        temperature=0.2,
        top_p=0.9,
    )
    return completion.choices[0].message.content

def answer_question(sources: List[str], card: str, question: str):    
    query_str = """A user has a question, given the information provided in the section THIS IS THE INFORMATION USER WAS GIVEN.
    Using the sources that I provide you, labeled by SOURCE, answer their question, labeled by QUESTION\n"""
    query_str += "SOURCES:"
    query_str += "\n_____________________________________________\n".join(sources)
    query_str += "\n_____________________________________________\n" 
    query_str += "THIS IS THE INFORMATION USER WAS GIVEN: \n"
    query_str += card
    query_str += "\n_____________________________________________\n" 
    query_str += "THIS IS THE USER'S QUESTION: " + "\n"
    query_str += question
    return mixtralGenerateText(query_str, 130)

