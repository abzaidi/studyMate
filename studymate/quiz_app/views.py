from django.shortcuts import render, HttpResponse, redirect
from .quiz_creation import generate_quizzes_from_text, process_file
from .qna_creation import generate_qna_from_text
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def home(request):
    context = {'page': 'home'}
    return render(request, "home.html", context)


def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, "User does not exists.")
        
        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "email or password is incorrect.")

    context = {'page': 'login'}
    return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect('login')


def registerPage(request):
    context = {'page': 'register'}
    return render(request, "login.html", context)

def features(request):
    context = {'page': 'features'}
    return render(request, "features.html", context)

def about(request):
    context = {'page': 'about'}
    return render(request, "about.html", context)

def contact(request):
    context = {'page': 'contact'}
    return render(request, "contact.html", context)

@login_required(login_url='login')
def main(request):
    cntx = {'page': 'main'}
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

        cntx.update({"extracted_text": extracted_text, 
                "generated_quizzes": generated_quizzes, 
                "generated_qna": generated_qna
                })  # Generate quizzes dynamically
    return render(request, "main.html", cntx)
