from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .quiz_creation import generate_quizzes_from_text, process_file
from .qna_creation import generate_qna_from_text
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt

from .models import User, ExtractedText, UserProfile
from .forms import MyUserCreationForm, UserProfileForm, CustomPasswordChangeForm
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

@login_required
def profile_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)  # Ensure profile exists

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        password_form = CustomPasswordChangeForm(user, request.POST)

        new_name = request.POST.get("name", "").strip()
        if new_name:
            user.name = new_name
            user.save()  # Save user model

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
        
        if request.POST.get("new_password1") and request.POST.get("new_password2"):
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.success(request, "Password updated successfully!")

        return redirect("profile")

    else:
        profile_form = UserProfileForm(instance=profile)
        password_form = CustomPasswordChangeForm(user)

    return render(request, "user_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })




@login_required(login_url='login')
def main(request):
    cntx = {'page': 'main'}
    generated_quizzes = ""
    generated_qna = ""
    extracted_text = ""
    gcs_url = None
    quiz_gcs_url = None
    qna_gcs_url = None

    # Get text_id from URL (if redirected from uploaded_content_detail)
    text_id = request.GET.get("text_id")
    extracted_obj = None

    if text_id:
        try:
            extracted_obj = ExtractedText.objects.get(id=text_id, user=request.user)
            extracted_text = fetch_text_from_gcs(extracted_obj.gcs_url) if extracted_obj.gcs_url else ""
        except ExtractedText.DoesNotExist:
            return HttpResponseNotFound("Extracted text not found.")

    if request.method == "POST":
        if "upload_file" in request.POST:
            input_file = request.FILES.get("input_file")  
            if input_file:
                file_path = default_storage.save(input_file.name, input_file)
                absolute_path = default_storage.path(file_path)
                extracted_text = process_file(absolute_path)

                # Save extracted text to database and get its ID
                extracted_obj = ExtractedText.objects.create(
                    user=request.user, file_name=input_file.name
                )

                extracted_filename = f"{extracted_obj.id}_extracted_text"
                gcs_url = upload_to_gcs(extracted_filename, extracted_text, file_type="extracted_texts")

                # Update database with GCS URL
                extracted_obj.gcs_url = gcs_url
                extracted_obj.save()

                default_storage.delete(file_path)

        elif "generate_quiz" in request.POST:
            extracted_text = request.POST.get("extracted_text", "")
            if extracted_text:
                generated_quizzes = generate_quizzes_from_text(extracted_text) or ""

                if not generated_quizzes:
                    return JsonResponse({"error": "No quiz content generated."}, status=400)

                # Ensure extracted_obj exists (either from previous step or fetch latest)
                if not extracted_obj:
                    extracted_obj = ExtractedText.objects.filter(user=request.user).latest("uploaded_at")

                quiz_filename = f"{extracted_obj.id}_quiz"
                quiz_gcs_url = upload_to_gcs(quiz_filename, generated_quizzes, file_type="quizzes")

                # Update database entry
                extracted_obj.quiz_gcs_url = quiz_gcs_url
                extracted_obj.save()

        elif "generate_qa" in request.POST:
            extracted_text = request.POST.get("extracted_text", "")
            if extracted_text:
                generated_qna = generate_qna_from_text(extracted_text)

                if not generated_qna:
                    return JsonResponse({"error": "No Q&A content generated."}, status=400)

                # Ensure extracted_obj exists
                if not extracted_obj:
                    extracted_obj = ExtractedText.objects.filter(user=request.user).latest("uploaded_at")

                qna_filename = f"{extracted_obj.id}_qna"
                qna_gcs_url = upload_to_gcs(qna_filename, generated_qna, file_type="qna")

                # Update database entry
                extracted_obj.qna_gcs_url = qna_gcs_url
                extracted_obj.save()

    # Ensure extracted_obj is updated in context
    cntx.update({
        "text_id": extracted_obj.id if extracted_obj else None,
        "extracted_text": extracted_text,
        "generated_quizzes": generated_quizzes,
        "generated_qna": generated_qna,
        "quiz_gcs_url": quiz_gcs_url or (extracted_obj.quiz_gcs_url if extracted_obj else None),
        "qna_gcs_url": qna_gcs_url or (extracted_obj.qna_gcs_url if extracted_obj else None)
    })

    return render(request, "main.html", cntx)




@login_required(login_url='login')
def user_extracted_texts(request):
    query = request.GET.get('q', '')

    # Fetch text metadata
    extracted_texts = ExtractedText.objects.filter(user=request.user).only(
        "id", "file_name", "gcs_url", "uploaded_at"
    )

    # Fetch all extracted texts, quizzes, and Q&A in parallel
    def fetch_data(text_entry):
        try:
            text_entry.extracted_text = fetch_text_from_gcs(text_entry.gcs_url)
        except FileNotFoundError:
            text_entry.extracted_text = "[Error: File not found in GCS]"
        return text_entry

    with ThreadPoolExecutor() as executor:
        extracted_texts = list(executor.map(fetch_data, extracted_texts))

    # Convert QuerySet to JSON-serializable list
    extracted_texts_list = [
        {
            "id": text.id,
            "file_name": text.file_name,
            "extracted_text": text.extracted_text,
            "uploaded_at": text.uploaded_at.strftime("%Y-%m-%d %H:%M"),
        }
        for text in extracted_texts
    ]

    # AJAX response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'texts': extracted_texts_list})

    # Render template
    return render(request, "uploaded_content.html", {
        "extracted_texts": extracted_texts_list,
        "query": query,
    })

@login_required(login_url='login')
def user_extracted_text_detail(request, text_id):
    try:
        text_entry = ExtractedText.objects.get(id=text_id, user=request.user)

        # Fetch extracted text, quiz, and Q&A content
        extracted_text = fetch_text_from_gcs(text_entry.gcs_url)
        quiz_text = fetch_text_from_gcs(text_entry.quiz_gcs_url) if text_entry.quiz_gcs_url else "No Quizzes generated yet."
        qna_text = fetch_text_from_gcs(text_entry.qna_gcs_url) if text_entry.qna_gcs_url else "No QnAs generated yet."

        context = {
            "text_entry": text_entry,
            "extracted_text": extracted_text,
            "quiz_text": quiz_text,
            "qna_text": qna_text,
        }

        return render(request, "uploaded_content_detail.html", context)

    except ExtractedText.DoesNotExist:
        return HttpResponseNotFound("Note not found")



@csrf_exempt
def delete_uploaded_content(request, text_id):
    if request.method == "DELETE":
        text = get_object_or_404(ExtractedText, id=text_id)
        text.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

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