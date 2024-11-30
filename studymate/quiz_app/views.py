from django.shortcuts import render, HttpResponse
from .quiz_creation import generate_quizzes

# Create your views here.

def home(request):
    return HttpResponse("This is the home page!!")


def loginPage(request):
    return HttpResponse("This is the login page!!")


def registerPage(request):
    return HttpResponse("This is the registration page!!")


def main(request):
    generated_quizzes = ""
    if request.method == "POST":
        input_text = request.POST.get("input_text")  # Get the input text from the form
        if input_text:
            generated_quizzes = generate_quizzes(input_text)  # Generate quizzes dynamically
    return render(request, "main.html", {"generated_quizzes": generated_quizzes})
