from django.shortcuts import render, HttpResponse, redirect
from .quiz_creation import generate_quizzes_from_text, process_file
from .qna_creation import generate_qna_from_text
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse

from .models import User, ExtractedText
from .forms import MyUserCreationForm
from .utils import upload_to_gcs, fetch_text_from_gcs
from concurrent.futures import ThreadPoolExecutor

# Create your views here.

def home(request):
    context = {'page': 'home'}
    return render(request, "home.html", context)


def redirect_to_register(request):
    email = request.GET.get("email", "")
    if email:
        return redirect(f"/register/?email={email}")
    return redirect("register") 

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
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


# def registerPage(request):
#     form = MyUserCreationForm()
#     if request.method == 'POST':
#         form = MyUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.email = user.email.lower()
#             user.save()
#             login(request, user)
#             return redirect('home')
#         else:
#             messages.error(request, "An error occurred during registration.")

#     context = {'form': form}
#     return render(request, "login.html", context)

def registerPage(request):
    email_prefill = request.GET.get("email", "") 
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # Specify the custom EmailBackend explicitly
                login(request, user, backend='quiz_app.backends.EmailBackend')
                return redirect('home')
        else:
            messages.error(request, "An error occurred during registration.")
    else:
        form = MyUserCreationForm(initial={"email": email_prefill})
    context = {'form': form}
    return render(request, 'login.html', context)


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
    gcs_url = None
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
                # Upload the extracted text to Google Cloud Storage
                gcs_url = upload_to_gcs(input_file.name, extracted_text)
                # Save the fine name and its GCS URL to the database
                ExtractedText.objects.create(user=request.user, file_name=input_file.name, gcs_url=gcs_url)
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
        
    if gcs_url:
        extracted_text = fetch_text_from_gcs(gcs_url)

    cntx.update({"extracted_text": extracted_text, 
            "generated_quizzes": generated_quizzes, 
            "generated_qna": generated_qna,
            })  # Generate quizzes dynamically
    return render(request, "main.html", cntx)


@login_required
def user_extracted_texts(request):
    query = request.GET.get('q', '')
    if query:
        extracted_texts = ExtractedText.objects.filter(user=request.user, file_name__icontains=query)
    else:
        extracted_texts = ExtractedText.objects.filter(user=request.user)

    # Fetch all texts from GCS in parallel using ThreadPoolExecutor
    def fetch_text(text_entry):
        try:
            text_entry.extracted_text = fetch_text_from_gcs(text_entry.gcs_url)
        except FileNotFoundError:
            text_entry.extracted_text = "[Error: File not found in Google Cloud Storage]"
        return text_entry

    with ThreadPoolExecutor() as executor:
        extracted_texts = list(executor.map(fetch_text, extracted_texts))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('uploaded_content_partial.html', {'extracted_texts': extracted_texts, 'query': query})
        return HttpResponse(html)

    return render(request, "uploaded_content.html", {
        "extracted_texts": extracted_texts,
        "query": query,
    })


def send_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        terms = request.POST.get('terms')

        if terms:
            send_mail(
                f'Message from {name}',
                message,
                email,
                ['abubakar.zaidi03@gmail.com'],  # replace with your email
                fail_silently=False,
            )
            messages.success(request, "Email sent successfully.")
            return redirect('home')
        else:
            messages.error(request, "Please accept the terms and conditions.")
    return HttpResponse('Failed to send email')