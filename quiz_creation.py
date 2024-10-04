import os
import openai
from dotenv import load_dotenv, find_dotenv
from together import Together

_ = load_dotenv(find_dotenv())


client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

# Function to call the LLaMA 3 API and generate quizzes for a given text
def quiz_creation(page_text):
    # System prompt to instruct the model on what it should do
    system_prompt = """You are an AI quiz generator. Your job is to create multiple-choice quizzes 
        from the provided text to help students prepare for exams. Focus on the important, 
        meaningful information in the text and ignore any irrelevant details. Each quiz 
        should include one question, one correct answer, and three distractor options.
        if there is not enough information to generate a question or correct answer
        or distractor then simply do not attempt to generate a quiz from that information.
        Depending on the amount of important information, generate between 1 to 5 quizzes per page.
        Do not create quizzes with the same information more than one time, try to make each quiz unique
        from the other quiz. Please ensure the output is clean and simple, without any additional 
        commentary or explanations. Do not include phrases like 'Here are 2 quizzes based on the provided text:' etc.
        The format for each quiz should be:\n\n
        Question: <Question>\n
        1. <Option 1>\n
        2. <Option 2>\n
        3. <Option 3>\n
        4. <Option 4>\n
        Correct Answer: <Correct Option>"""
    
    # User prompt - the actual page content (text) that is used for generating the quiz
    user_prompt = f"Text:\n{page_text}\n\nGenerate 1-5 quizzes based on the meaningful information."

    # Make the API call to LLaMA 3 for quiz generation
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                    "role": "user",
                    "content": user_prompt
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

    # Extract the generated quizzes from the response
    quizzes = response.choices[0].message.content.strip()
    
    return quizzes

# Function to read the text file page by page and generate quizzes for each page
def generate_quizzes_from_file(file_path, page_size=1000):
    with open(file_path, 'r') as file:
        text = file.read()

    # Split the text into chunks (pages) of a given size
    pages = [text[i:i+page_size] for i in range(0, len(text), page_size)]

    all_quizzes = []

    # Generate quizzes for each page
    for i, page in enumerate(pages):
        print(f"Generating quizzes for page {i+1}...")
        quizzes = quiz_creation(page)
        all_quizzes.append(f"\n{quizzes}\n\n")

    return all_quizzes

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
    quizzes = generate_quizzes_from_file(input_file)
    
    # Write the quizzes to an output file
    write_quizzes_to_file(output_file, quizzes)
