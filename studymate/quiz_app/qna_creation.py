import os
import openai
from dotenv import load_dotenv, find_dotenv
from together import Together

_ = load_dotenv(find_dotenv())


llama_client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

def qna_creation(page_text):
    # System prompt to instruct the model on what it should do
    system_prompt =  """You are an AI system that generates short question-answer pairs from the provided text. 
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
        Do not include phrases like 'Here are 2 question-answer pair based on the provided text:' 
        etc.
        The format for each question-answer pair should be:\n\n"
        Q: <Question>\n"
        A: <Answer (one or two paragraphs)>"""
    
    # User prompt - the actual page content (text) that is used for generating the quiz
    user_prompt = f"Text:\n{page_text}\n\nGenerate question-answer pairs based on the meaningful information."

    # Make the API call to LLaMA 3 for quiz generation
    response = llama_client.chat.completions.create(
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
    qna = response.choices[0].message.content.strip()
    
    return qna

def generate_qna_from_text(text, page_size=1000):

    # Split the text into chunks (pages) of a given size
    pages = [text[i:i+page_size] for i in range(0, len(text), page_size)]

    all_qna = []

    # Generate quizzes for each page
    for i, page in enumerate(pages):
        print(f"Generating qna's for page {i+1}...")
        qna = qna_creation(page)
        all_qna.append(f"\n{qna}\n\n")

    return "".join(all_qna)