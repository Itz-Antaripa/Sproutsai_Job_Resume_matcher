from openai import OpenAI
import openai
from config import *

client = OpenAI(
        api_key=OPENAI_API_KEY,
    )


def get_answer_from_openai(conversation_prompt, model_engine=GPT_3, temperature=temperature, top_p=top_p):
    try:
        completion = client.chat.completions.create(
            model=model_engine,
            messages=conversation_prompt,
            temperature=temperature,
            top_p=top_p
        )
        response_text = completion.choices[0].message.content

    except Exception as e:
        response_text = f"Sorry we were not able to generate the response because of exception {e}"

    return response_text


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    embeddings = response.data[0].embedding
    return embeddings
