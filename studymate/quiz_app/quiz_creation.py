import os
import openai
from dotenv import load_dotenv, find_dotenv
from together import Together

_ = load_dotenv(find_dotenv())


client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))


def generate_quizzes(page_text):
    # System prompt to instruct the model on what it should do
    system_prompt = """You are an AI quiz generator. Your job is to create multiple-choice quizzes 
        from the provided text to help students prepare for exams. Focus on the important, 
        meaningful information in the text and ignore any irrelevant details. Each quiz 
        should include one question, one correct answer, and three distractor options.
        Each distractor should be plausible and relevant to the correct answer but could be misleading
        and different in length. The correct answer should be randomly placed among the four options.
        The quiz should be clear, concise, and well-structured to test the students' understanding of the text
        and the question should provide complete information without requiring outside knowledge or context.
        If there is not enough information to generate a question or correct answer
        or distractor then simply do not attempt to generate a quiz from that information.
        Depending on the amount of important information, generate between 1 to 5 quizzes per page.
        Do not create quizzes with the same information more than one time, try to make each quiz unique
        from the other quiz. Please ensure the output is clean and simple, without any additional 
        commentary or explanations. Do not include phrases like 'Here are 2 quizzes based on the provided text:' etc.
        The format for each quiz should be:\n\n
        Question: <Question>\n
        a. <Option 1>\n
        b. <Option 2>\n
        c. <Option 3>\n
        d. <Option 4>\n
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
        temperature=0.8,
        top_p=0.9,
        top_k=50,
        repetition_penalty=1.1,
        stop=["<|eot_id|>","<|eom_id|>"],
        stream=False
    )

    # Extract the generated quizzes from the response
    quizzes = response.choices[0].message.content.strip()
    
    return quizzes