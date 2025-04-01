import os
import openai
from dotenv import load_dotenv, find_dotenv
from together import Together
from PIL import Image
from google.cloud import vision
from pdf2image import convert_from_path
import io

_ = load_dotenv(find_dotenv())


llama_client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

google_credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if google_credentials_path is None:
    raise ValueError("The environment variable 'GOOGLE_APPLICATION_CREDENTIALS' is not set.")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_credentials_path

def convert_pdf_to_images(pdf_path):
    try:
        return convert_from_path(pdf_path)
    except Exception as e:
        raise RuntimeError(f"Error converting PDF to images: {e}")

def image_to_byte_array(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def extract_text_from_image(image_content):
    # Initialize the Vision API client
    vision_client = vision.ImageAnnotatorClient()

    # Construct an image instance
    image = vision.Image(content=image_content)

    # Perform text detection
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    # Extract the detected text
    if texts:
        extracted_text = texts[0].description
    else:
        extracted_text = ""

    # Handle possible errors
    if response.error.message:
        raise Exception(f'{response.error.message}')

    return extracted_text


def correct_grammar_and_context(text):
    system_prompt = """
    You are an advanced language model. Your task is to correct the grammar,
    structure, and spelling of the provided text. Please ensure the output is
    clean and simple, without any additional commentary or explanations.
    Do not include phrases like 'Here is the corrected text:' or 'I made the following changes:' or 
    'Note: I have made the following changes to the original text: etc.
    """

    response = llama_client.chat.completions.create(
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

def process_file(file_path):
    all_text = ""

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Check if the file is a PDF or an image
    if file_path.lower().endswith('.pdf'):
        # Convert PDF to images
        images = convert_pdf_to_images(file_path)
    elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        # Open the image file
        images = [Image.open(file_path)]
    else:
        raise ValueError("Unsupported file format. Please provide a PDF, PNG, or JPG file.")

    for i, image in enumerate(images):
        # Convert image to byte array
        img_byte_arr = image_to_byte_array(image)

        # Extract text from image
        text = extract_text_from_image(img_byte_arr)

        # Clean the extracted text
        # text = normalize_text(text)
        text = correct_grammar_and_context(text)


        all_text += f"{text}\n\n"

    return all_text


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
    quizzes = response.choices[0].message.content.strip()
    
    return quizzes


def generate_quizzes_from_text(text, page_size=1000):

    # Split the text into chunks (pages) of a given size
    pages = [text[i:i+page_size] for i in range(0, len(text), page_size)]

    all_quizzes = []

    # Generate quizzes for each page
    for i, page in enumerate(pages):
        print(f"Generating quizzes for page {i+1}...")
        quizzes = generate_quizzes(page)
        all_quizzes.append(f"\n{quizzes}\n\n")

    return "".join(all_quizzes)


def generate_quizzes_with_topics(page_text, selected_topics):
    # System prompt to instruct the model on what it should do, now focusing on the selected topics
    system_prompt = """You are an AI quiz generator. Your job is to create multiple-choice quizzes 
        from the provided text, but only focus on the selected topics. The quizzes should test the students' understanding
        of the important information related to those topics, and ignore irrelevant details.
        Each quiz should include one question, one correct answer, and three distractor options.
        Each distractor should be plausible and relevant to the correct answer but could be misleading
        and different in length. The correct answer should be randomly placed among the four options.
        The quiz should be clear, concise, and well-structured to test the students' understanding of the text.
        If there is not enough information to generate a question or correct answer or distractor, 
        simply do not attempt to generate a quiz from that information.
        Depending on the amount of important information, generate between 1 to 5 quizzes based on the selected topics.
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

    # Prepare a specific prompt based on the selected topics
    topics_str = ', '.join(selected_topics)
    user_prompt = f"Text:\n{page_text}\n\nSelected Topics: {topics_str}\n\nGenerate 1-5 quizzes based on the selected topics."

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
    quizzes = response.choices[0].message.content.strip()

    return quizzes


def generate_quizzes_from_topics(extracted_text, selected_topics, page_size=1000):
    # Split the text into chunks (pages) of a given size
    pages = [extracted_text[i:i+page_size] for i in range(0, len(extracted_text), page_size)]

    all_quizzes = []

    # Generate quizzes for each page, but only for the selected topics
    for i, page in enumerate(pages):
        print(f"Generating quizzes for page {i+1}...")
        quizzes = generate_quizzes_with_topics(page, selected_topics)
        all_quizzes.append(f"\n{quizzes}\n\n")

    return "".join(all_quizzes)