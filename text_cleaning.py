import re
import os
from dotenv import load_dotenv, find_dotenv
from together import Together

_ = load_dotenv(find_dotenv())


client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))


# def remove_unwanted_phrases(text):
#     patterns = [
#         r"Note:.*",  # Matches any line starting with "Note:"
#         r"Here is the corrected and enhanced text:.*",  # Matches any line starting with this phrase
#         r"I made several changes to the text, including:.*",  # Matches any line starting with this phrase
#         r"Here is the corrected text:.*",  # Matches any line starting with this phrase
#         r"I made the following changes:.*",  # Matches any line starting with this phrase
#         r"Corrected text.*",  # Matches any line starting with this phrase
#         r"Enhanced text.*",  # Matches any line starting with this phrase
#         r"Corrected spelling.*",  # Matches any line starting with this phrase
#         r"Corrected grammar.*",  # Matches any line starting with this phrase
#         r"Corrected punctuation.*",  # Matches any line starting with this phrase
#         r"Corrected capitalization.*",  # Matches any line starting with this phrase
#         r"Corrected formatting.*",  # Matches any line starting with this phrase
#         r"Corrected the date format.*",  # Matches any line starting with this phrase
#         r"Emphasized key points.*",  # Matches any line starting with this phrase
#         r"Added headings.*",  # Matches any line starting with this phrase
#         r"Improved sentence.*",  # Matches any line starting with this phrase
#     ]
    
#     combined_pattern = "|".join(patterns)
#     cleaned_text = re.sub(combined_pattern, "", text, flags=re.MULTILINE)
#     cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text).strip()
    
#     return cleaned_text

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
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters (optional)
    # text = re.sub(r'[^\w\s]', '', text)
    return text