from together import Together
from pydantic import BaseModel, Field
from dotenv import load_dotenv, find_dotenv
import os


_ = load_dotenv(find_dotenv())

llama_client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))


class TopicsResponse(BaseModel):
    topics: list[str] = Field(description="List of identified high-level topics")

def generate_topics(chunk):
    system_prompt = (
        "Identify 1-2 high-level topics from the provided text. "
        "Exclude any irrelevant content or phrases related to AI. "
        "Return the topics in a JSON array format."
    )

    user_prompt = f"Text:\n{chunk}\n\nGenerate 1-2 high-level topics based on the text."

    # Define the response format with the JSON schema
    response_format = {
        "type": "json_object",
        "schema": TopicsResponse.model_json_schema()
    }

    # Make the API call to Together AI for topic generation
    response = llama_client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=response_format,
        max_tokens=100,
        temperature=0.8,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    # Extract and parse the generated topics
    try:
        response_content = response.choices[0].message.content.strip()
        topics_json = TopicsResponse.model_validate_json(response_content)
        return topics_json.topics  # Return list of topics
    except Exception as e:
        print(f"Error parsing response: {e}")
        return []  # Return empty list if parsing fails


def generate_topics_from_file(text, chunk_size=1000):
    # Further processing can be done here
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_topics = []

    for i, chunk in enumerate(chunks):
        print(f"Generating topics for page {i+1}...")
        topics = generate_topics(chunk)
        all_topics.extend(topics)

    return all_topics