from django.shortcuts import render, HttpResponse
from .quiz_creation import generate_quizzes_from_text, process_file
from .qna_creation import generate_qna_from_text
from django.core.files.storage import default_storage

# Create your views here.

def home(request):
    return render(request, "home.html")


def loginPage(request):
    return render(request, "login.html")


def registerPage(request):
    return HttpResponse("This is the registration page!!")

def features(request):
    return render(request, "features.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")


def main(request):
    cntx = {}
    generated_quizzes = ""
    generated_qna = ""
    extracted_text = ""
    if request.method == "POST":
        if "upload_file" in request.POST:
            input_file = request.FILES.get("input_file")  # Get the input text from the form
            if input_file:
                # Save the uploaded file to the MEDIA_ROOT directory
                file_path = default_storage.save(input_file.name, input_file)
                # Get the absolute path of the saved file
                absolute_path = default_storage.path(file_path)
                # Process the file to extract text
                extracted_text = process_file(absolute_path)
                # Clean up the temporary file
                default_storage.delete(file_path)
        elif "generate_quiz" in request.POST:
            # Get extracted text from the hidden input
            extracted_text = request.POST.get("extracted_text", "")
            if extracted_text:
                # Generate quizzes from the extracted text
                generated_quizzes = generate_quizzes_from_text(extracted_text)
        elif "generate_qa" in request.POST:
            # Get extracted text from the hidden input
            extracted_text = request.POST.get("extracted_text", "")
            if extracted_text:
                # Generate Q&A pairs from the extracted text
                generated_qna = generate_qna_from_text(extracted_text)

        cntx = {"extracted_text": extracted_text, "generated_quizzes": generated_quizzes, "generated_qna": generated_qna}  # Generate quizzes dynamically
    return render(request, "main.html", cntx)
