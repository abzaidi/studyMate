from django.shortcuts import render, HttpResponse
from .quiz_creation import generate_quizzes, process_file
from django.core.files.storage import default_storage

# Create your views here.

def home(request):
    return HttpResponse("This is the home page!!")


def loginPage(request):
    return HttpResponse("This is the login page!!")


def registerPage(request):
    return HttpResponse("This is the registration page!!")


def main(request):
    cntx = {}
    generated_quizzes = ""
    extracted_text = ""
    if request.method == "POST":
        input_file = request.FILES.get("input_file")  # Get the input text from the form
        if input_file:
            file_path = default_storage.save(input_file.name, input_file)
            absolute_path = default_storage.path(file_path)
            extracted_text = process_file(absolute_path)
            generated_quizzes = generate_quizzes(extracted_text)
            default_storage.delete(file_path)
            cntx = {"extracted_text": extracted_text, "generated_quizzes": generated_quizzes}  # Generate quizzes dynamically
    return render(request, "main.html", cntx)
