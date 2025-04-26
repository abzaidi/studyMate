import os
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
# def quiz_creation(page_text):
#     # System prompt to instruct the model on what it should do
#     system_prompt = """You are an AI quiz generator. Your job is to create multiple-choice quizzes 
#         from the provided text to help students prepare for exams. Focus on the important, 
#         meaningful information in the text and ignore any irrelevant details. Each quiz 
#         should include one question, one correct answer, and three distractor options.
#         Each distractor should be plausible and relevant to the correct answer but could be misleading
#         and different in length. The correct answer should be randomly placed among the four options.
#         The quiz should be clear, concise, and well-structured to test the students' understanding of the text
#         and the question should provide complete information without requiring outside knowledge or context.
#         If there is not enough information to generate a question or correct answer
#         or distractor then simply do not attempt to generate a quiz from that information.
#         Depending on the amount of important information, generate between 1 to 5 quizzes per page.
#         Do not create quizzes with the same information more than one time, try to make each quiz unique
#         from the other quiz. Please ensure the output is clean and simple, without any additional 
#         commentary or explanations. Do not include phrases like 'Here are 2 quizzes based on the provided text:' etc.
#         The format for each quiz should be:\n\n
#         Question: <Question>\n
#         a. <Option 1>\n
#         b. <Option 2>\n
#         c. <Option 3>\n
#         d. <Option 4>\n
#         Correct Answer: <Correct Option>"""
    
#     # User prompt - the actual page content (text) that is used for generating the quiz
#     user_prompt = f"Text:\n{page_text}\n\nGenerate 1-5 quizzes based on the meaningful information."

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
#     quizzes = response.choices[0].message.content.strip()
    
#     return quizzes

# # Function to read the text file page by page and generate quizzes for each page
# def generate_quizzes_from_file(file_path, page_size=1000):
#     with open(file_path, 'r') as file:
#         text = file.read()

#     # Split the text into chunks (pages) of a given size
#     pages = [text[i:i+page_size] for i in range(0, len(text), page_size)]

#     all_quizzes = []

#     # Generate quizzes for each page
#     for i, page in enumerate(pages):
#         print(f"Generating quizzes for page {i+1}...")
#         quizzes = quiz_creation(page)
#         all_quizzes.append(f"\n{quizzes}\n\n")

#     return all_quizzes


class Quiz(BaseModel):
    question: str
    options: list[str] = Field(min_items=4, max_items=4, description="Four options for the question")
    correct_option: int = Field(description="Index (0-3) of the correct option")

class QuizzesResponse(BaseModel):
    quizzes: list[Quiz]

def generate_quizzes(chunk):
    system_prompt = (
        """You are an AI quiz generator. Your job is to create multiple-choice quizzes 
            from the provided text to help students prepare for exams. Focus on the important, 
            meaningful information in the text and ignore any irrelevant details.
            Each distractor should be plausible and relevant to the correct answer but could be misleading
            and different in length. The correct answer should be randomly placed among the four options.
            The quiz should be clear, concise, and well-structured to test the students' understanding of the text
            and the question should provide complete information without requiring outside knowledge or context.
            If there is not enough information to generate a question or correct answer
            or distractor then simply do not attempt to generate a quiz from that information.
            Depending on the amount of important information, generate between 1 to 5 quizzes per page.
            Do not create quizzes with the same information more than one time, try to make each quiz unique
            from the other quiz. Please ensure the output is clean and simple, without any additional 
            commentary or explanations. Generate 1-5 multiple-choice questions from the provided text.
            Each question must have exactly four options and a correct option index (0-3).
            Return the quizzes in a JSON format where each quiz has 'question', 'options' (list of 4 options), and 'correct_option' (integer index of correct option)."""
        )

    user_prompt = f"Text:\n{chunk}\n\nCreate 1-5 MCQs based on important information from the text."

    response_format = {
        "type": "json_object",
        "schema": QuizzesResponse.model_json_schema()
    }

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=response_format,
        max_tokens=1000,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.1,
        stop=["<|eot_id|>", "<|eom_id|>"],
        stream=False
    )

    try:
        response_content = response.choices[0].message.content.strip()
        quizzes_json = QuizzesResponse.model_validate_json(response_content)
        return quizzes_json.quizzes  # Return a list of Quiz objects
    except Exception as e:
        print(f"Error parsing quizzes response: {e}")
        return []

def generate_quizzes_from_text(text, chunk_size=1000):
    with open(text, 'r', encoding='UTF-8') as file:
        file_contents = file.read()

    chunks = [file_contents[i:i+chunk_size] for i in range(0, len(file_contents), chunk_size)]
    all_quizzes = []

    for i, chunk in enumerate(chunks):
        print(f"Generating quizzes for chunk {i+1}...")
        quizzes = generate_quizzes(chunk)
        all_quizzes.extend(quizzes)

    return all_quizzes


def parse_quizzes(raw_response):
    quizzes = []

    # Match each Quiz(...) block
    pattern = r"Quiz\(question='(.*?)', options=\[(.*?)\], correct_option=(\d+)\)"
    matches = re.findall(pattern, raw_response, re.DOTALL)

    for match in matches:
        question = match[0]
        options_str = match[1]
        correct_option = int(match[2])

        # Safely convert options list from string
        options = ast.literal_eval(f"[{options_str}]")

        quizzes.append({
            'question': question,
            'options': options,
            'correct_option': correct_option
        })

    return quizzes


def convert_quiz_objects_to_json(quiz_objects):
    """Convert Python Quiz object representations to proper JSON format"""
    json_output = []
    
    for quiz in quiz_objects:
        # Convert Quiz object to dictionary
        quiz_dict = {
            "question": quiz.question,
            "options": [option.strip() for option in quiz.options],
            "correct_option": quiz.correct_option
        }
        json_output.append(quiz_dict)
    
    json_string = json.dumps(json_output, indent=2)
    return json_string
# Function to write generated quizzes to an output file
def write_quizzes_to_file(output_file, quizzes):
    with open(output_file, 'w') as file:
        file.writelines(quizzes)
    print(f"Quizzes successfully written to {output_file}.")

# Example usage
if __name__ == "__main__":
    input_file = "extracted_texts/extracted_text.txt"  # The input text file with the material
    output_file = "generated_quizzes.txt"  # The output file to store generated quizzes
    
    # Generate quizzes from the input file
    quizzes = generate_quizzes_from_text(input_file)
    parsed_quizzes = convert_quiz_objects_to_json(quizzes)
    print(parsed_quizzes)
    # Write the quizzes to an output file
    # write_quizzes_to_file(output_file, quizzes)
