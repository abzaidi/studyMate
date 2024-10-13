import re
import os
from dotenv import load_dotenv, find_dotenv
from together import Together

_ = load_dotenv(find_dotenv())


client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

def correct_grammar_and_context(text):
    system_prompt = """
    You are an advanced language model. Your task is to correct the grammar,
    structure, and spelling of the provided text. Please ensure the output is
    clean and simple, without any additional commentary or explanations.
    Do not include phrases like 'Here is the corrected text:' or 'I made the following changes:' etc.
    """

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                    "role": "user",
                    "content": f"correct and enhance the following the text:\n\n{text}"
            },
        ],
        max_tokens=1000,
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=False
    )
    return response.choices[0].message.content


def normalize_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text