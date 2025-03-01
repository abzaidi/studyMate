
# StudyMate

StudyMate is an innovative platform that streamlines learning by converting handwritten notes into structured digital content. It utilizes advanced OCR
technology, AI-based grammar refinement, and quiz generation algorithms to create personalized study materials. Designed for students and educators,
StudyMate aims to enhance academic preparation with minimal effort and
maximum accuracy.




## Features
- Allows students and teachers to upload handwritten notes in various formats (PDF, JPG, PNG).
- Extracts and refines the text using Google Vision OCR and Llama 3.1.
- Generates quizzes and Q&A content based on user preferences using "meta-llama/MetaLlama-3.1-8B-Instruct-Turbo."
- Offers user-friendly templates for Home, Login, Register, and Quiz/Q&A generation pages.
- Future iterations may include user authentication, database functionality, and additional features.



## Tech Stack

**Client:** HTML, CSS, Javascript, Jinja

**Server:** Django, SQL

**APIs:** Llama 3.1 by TogetherAI, Google Vision OCR

## Architecture

![Logo](https://i.imgur.com/366E7jo.png)

## Run Locally

Clone the project

```bash
  git clone https://github.com/abzaidi/studyMate.git
```

Go to the project directory

```bash
  cd studymate
```

Set up and activate virtual environment

```bash
  python -m venv venv
  venv\Scripts\activate
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Set up environment variables:

- Create a .env file in the project root directory.

- Enable Google Vision API in Google Cloud Console and generate the JSON API key file using a service account and place that file in the root directory of the project.

- Create a new bucket in google cloud storage with the name "save-notes-to-cloud" and make it public.

- Add the necessary environment variables, such as TOGETHER_API_KEY and GOOGLE_APPLICATION_CREDENTIALS.

```bash
  GOOGLE_APPLICATION_CREDENTIALS=F:/Path/To/Your/Vision/API/Key/File
  TOGETHER_API_KEY = abcdefgijklmnopqrstuvwxyz
```

- Install Poppler and include its bin folder file path to the system environment variables.

Go to the project django directory

```bash
  cd studymate
```
Apply database migrations

```bash
  python manage.py migrate
```

Run the development server

```bash
  python manage.py runserver
```

Access the application

- Open a web browser and go to http://127.0.0.1:8000.

