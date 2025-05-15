import os
import openai
from dotenv import load_dotenv, find_dotenv
from together import Together
from pydantic import BaseModel, Field
from typing import List
import re
import ast
import json

_ = load_dotenv(find_dotenv())


client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

# Function to call the LLaMA 3 API and generate quizzes for a given text
# def qna_creation(page_text):
#     # System prompt to instruct the model on what it should do
#     system_prompt =  """You are an AI system that generates short question-answer pairs from the provided text. 
#         Focus on important and meaningful information, summarizing key points to create a question 
#         and a corresponding answer. The answer should be concise, ideally no longer than two paragraphs, 
#         and should cover the essential information related to the question. The purpose is to help students 
#         prepare for exams by providing answers that are informative but to the point.
#         If there is not enough information to generate a question or answer
#         then simply do not attempt to generate a question-answer pair from that information.
#         Depending on the amount of important information, generate between 1 to 5 question-answer pair per page.
#         Do not create question-answer pairs with the same information more than one time, try to make each 
#         question-answer pair unique from the other question-answer pair. If the provided text lacks sufficient 
#         information to answer a question completely, use your own knowledge to fill in the details, ensuring 
#         the answer is complete and accurate. However, prioritize information in the text first. 
#         Please ensure the output is clean and simple, without any additional commentary or explanations. 
#         Do not include phrases like 'Here are 2 question-answer pair based on the provided text:' etc.
#         The format for each question-answer pair should be:\n\n"
#         Q: <Question>\n"
#         A: <Answer (one or two paragraphs)>"""
    
#     # User prompt - the actual page content (text) that is used for generating the quiz
#     user_prompt = f"Text:\n{page_text}\n\nGenerate question-answer pairs based on the meaningful information."

#     # Make the API call to LLaMA 3 for quiz generation
#     response = client.chat.completions.create(
#         model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
#         messages=[
#             {
#                 "role": "system",
#                 "content": system_prompt
#             },
#             {
#                     "role": "user",
#                     "content": user_prompt
#             },
#         ],
#         max_tokens=1000,
#         temperature=0.8,
#         top_p=0.9,
#         top_k=50,
#         repetition_penalty=1.1,
#         stop=["<|eot_id|>","<|eom_id|>"],
#         stream=False
#     )

#     # Extract the generated quizzes from the response
#     qna = response.choices[0].message.content.strip()
    
#     return qna

# # Function to read the text file page by page and generate quizzes for each page
# def generate_qna_from_file(file_path, page_size=1000):
#     with open(file_path, 'r') as file:
#         text = file.read()

#     # Split the text into chunks (pages) of a given size
#     pages = [text[i:i+page_size] for i in range(0, len(text), page_size)]

#     all_qna = []

#     # Generate quizzes for each page
#     for i, page in enumerate(pages):
#         print(f"Generating qna's for page {i+1}...")
#         qna = qna_creation(page)
#         all_qna.append(f"\n{qna}\n\n")

#     return all_qna

# # Function to write generated quizzes to an output file
# def write_qna_to_file(output_file, qna):
#     with open(output_file, 'w') as file:
#         file.writelines(qna)
#     print(f"QnA's successfully written to {output_file}.")


class QnAPair(BaseModel):
    question: str = Field(description="The generated question")
    answer: str = Field(description="The corresponding answer to the question")

class QnAResponse(BaseModel):
    qna_pairs: list[QnAPair] = Field(description="List of question-answer pairs")

def qna_creation(page_text):
    system_prompt = """You are an AI system that generates short question-answer pairs from the provided text. 
         Focus on important and meaningful information, summarizing key points to create a question 
         and a corresponding answer. The answer should be concise, ideally no longer than two paragraphs, 
         and should cover the essential information related to the question. The purpose is to help students 
         prepare for exams by providing answers that are informative but to the point.
         If there is not enough information to generate a question or answer
         then simply do not attempt to generate a question-answer pair from that information.
         Depending on the amount of important information, generate between 1 to 5 question-answer pair per page.
         Do not create question-answer pairs with the same information more than one time, try to make each 
         question-answer pair unique from the other question-answer pair. If the provided text lacks sufficient 
         information to answer a question completely, use your own knowledge to fill in the details, ensuring 
         the answer is complete and accurate. However, prioritize information in the text first. 
         Please ensure the output is clean and simple, without any additional commentary or explanations.
         Use clean JSON format with 'qna_pairs' array containing objects with 'question' and 'answer'
        
        Return ONLY valid JSON in this structure:
        {
            "qna_pairs": [
                {
                    "question": "clear question text",
                    "answer": "concise answer text"
                },
                // more pairs...
            ]
        }"""
    
    user_prompt = f"Text:\n{page_text}\nGenerate structured Q&A pairs from this text."

    response_format = {
        "type": "json_object",
        "schema": QnAResponse.model_json_schema()
    }

    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format,
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            stop=["<|eot_id|>", "<|eom_id|>"],
            stream=False
        )

        response_content = response.choices[0].message.content.strip()
        qna_response = QnAResponse.model_validate_json(response_content)
        return qna_response.qna_pairs

    except Exception as e:
        print(f"Error generating Q&A: {e}")
        # Fallback to text parsing if JSON fails
        return parse_text_fallback(response.choices[0].message.content.strip())

def parse_text_fallback(text_response):
    """Fallback method to parse text format Q&A"""
    qna_pairs = []
    current_q = None
    
    for line in text_response.split('\n'):
        line = line.strip()
        if line.startswith('Q:'):
            current_q = line[2:].strip()
        elif line.startswith('A:'):
            if current_q:
                qna_pairs.append(QnAPair(
                    question=current_q,
                    answer=line[2:].strip()
                ))
                current_q = None
    return qna_pairs

def convert_qna_objects_to_json(qna_objects):
    """Convert QnAPair objects to JSON string"""
    return json.dumps(
        [{"question": q.question, "answer": q.answer} for q in qna_objects],
        indent=2
    )

def generate_qna_from_text(text, chunk_size=1000):
    with open(text, 'r', encoding='UTF-8') as file:
        file_contents = file.read()
    chunks = [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]
    all_qna = []

    for chunk in chunks:
        try:
            qna_pairs = qna_creation(chunk)
            all_qna.extend(qna_pairs)
        except Exception as e:
            print(f"Error processing chunk: {e}")

    return convert_qna_objects_to_json(all_qna)

# Example usage
if __name__ == "__main__":
    input_file = "extracted_texts/extracted_text.txt"  # The input text file with the material
    output_file = "generated_qna/generated_qna.txt"  # The output file to store generated quizzes
    
    # Generate quizzes from the input file
    qna = generate_qna_from_text(input_file)
    
    # Write the quizzes to an output file
    print(qna)
