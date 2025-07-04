from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from .quiz_creation import generate_quizzes_from_text, generate_quizzes_from_topics ,process_file, convert_quiz_objects_to_json
from .qna_creation import generate_qna_from_text, generate_qna_from_topics
from .topics_generation import generate_topics_from_file
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt


from .models import User, ExtractedText, UserProfile
from .forms import MyUserCreationForm, UserProfileForm, CustomPasswordChangeForm
from .utils import upload_to_gcs, fetch_text_from_gcs
from concurrent.futures import ThreadPoolExecutor



# Create your views here.

def home(request):
    # messages.success(request, "Welcome to the home page!")
    context = {'page': 'home'}
    return render(request, "home.html", context)

@login_required(login_url='login')
def dashboard(request):
    if request.user.is_authenticated:
        split_entries = []
        # Get all ExtractedText entries ordered by latest first
        extracted_texts = ExtractedText.objects.filter(user=request.user).order_by('-uploaded_at')
        for et in extracted_texts:
            # Text entry (always present)
            text_entry = {
                'id': et.id,
                'file_name': et.file_name,
                'uploaded_at': et.uploaded_at,
                'gcs_url': et.gcs_url,
                'type': 'text'
            }
            split_entries.append(text_entry)
            if len(split_entries) >= 5:
                break
            
            # Quiz entry (if present)
            if et.quiz_gcs_url:
                quiz_entry = {
                    'id': et.id,
                    'file_name': et.file_name,
                    'uploaded_at': et.uploaded_at,
                    'quiz_gcs_url': et.quiz_gcs_url,
                    'type': 'quiz'
                }
                split_entries.append(quiz_entry)
                if len(split_entries) >= 5:
                    break
            
            # QnA entry (if present)
            if et.qna_gcs_url:
                qna_entry = {
                    'id': et.id,
                    'file_name': et.file_name,
                    'uploaded_at': et.uploaded_at,
                    'qna_gcs_url': et.qna_gcs_url,
                    'type': 'qna'
                }
                split_entries.append(qna_entry)
                if len(split_entries) >= 5:
                    break
        
        # Ensure we only take up to five entries
        split_entries = split_entries[:5]
        notes_count = ExtractedText.objects.filter(user=request.user).count()
        quizzes_count = ExtractedText.objects.filter(user=request.user, quiz_gcs_url__isnull=False).count()
        qna_count = ExtractedText.objects.filter(user=request.user, qna_gcs_url__isnull=False).count()
        context = {
            'page': 'dashboard',
            'split_entries': split_entries,
            'notes_count': notes_count,
            'quizzes_count': quizzes_count,
            'qna_count': qna_count,
        }
    return render(request, "dashboard.html", context)

def redirect_to_register(request):
    email = request.GET.get("email", "")
    if email:
        return redirect(f"/register/?email={email}")
    return redirect("register") 

def loginPage(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User Not Found|The user you are trying to access does not exist.")
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login Successful|You have successfully logged in! Welcome back!")
            return redirect('dashboard')
        else:
            messages.error(request, "Login Error|The email or password you entered is incorrect. Please try again.")

    context = {'page': 'login'}
    return render(request, "login.html", context)


def logoutUser(request):
    messages.success(request, "Logout Successful|You have been logged out successfully!")
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
                messages.success(request, "Registration Complete|Your registration was successful! Welcome to StudyMate!")
                return redirect('dashboard')
        else:
            messages.error(request, "Registration Error|An error occurred during registration. Please try again later.")
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
            messages.success(request, "Profile Updated|Your profile has been updated successfully!")
        
        if request.POST.get("new_password1") and request.POST.get("new_password2"):
            if password_form.is_valid():
                user.set_password(password_form.cleaned_data["new_password1"])
                user.save()
                update_session_auth_hash(request, user)  # Keep the user logged in
                messages.info(request, "Password Updated|Your password has been updated successfully!")

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
    generated_topics = request.session.get('generated_topics', [])
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
        selected_topics_str = request.POST.get("selected_topics", "")
        selected_topics = selected_topics_str.split(',') if selected_topics_str else []

        extracted_text = request.POST.get("extracted_text", "")
        if "upload_file" in request.POST:
            input_file = request.FILES.get("input_file")  
            if input_file:
                file_path = default_storage.save(input_file.name, input_file)
                absolute_path = default_storage.path(file_path)
                extracted_text = process_file(absolute_path)
                generated_topics = generate_topics_from_file(extracted_text)
                request.session['generated_topics'] = generated_topics
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
            if extracted_text:
                if not selected_topics or set(selected_topics) == set(generated_topics):
                    generated_quizzes = generate_quizzes_from_text(extracted_text) or ""
                    generated_quizzes = convert_quiz_objects_to_json(generated_quizzes) or ""
                else:
                    generated_quizzes = generate_quizzes_from_topics(extracted_text, selected_topics) or ""
                    generated_quizzes = convert_quiz_objects_to_json(generated_quizzes) or ""

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
            if extracted_text:
                if not selected_topics or set(selected_topics) == set(generated_topics):
                    generated_qna = generate_qna_from_text(extracted_text)
                else:
                    generated_qna = generate_qna_from_topics(extracted_text, selected_topics)

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
        "generated_topics": generated_topics,
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
            subject = f"📨 Message from {name}"
            from_email = 'ma2003110@gmail.com' 
            to_email = ['abubakar.zaidi03@gmail.com']

            html_content = f"""
            <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f9f9f9;">
                <h2 style="color: #007bff;">New Message from StudyMate</h2>
                <p style="font-size: 16px;"><strong>Name:</strong> {name}</p>
                <p style="font-size: 16px;"><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
                <p style="font-size: 16px;"><strong>Message:</strong></p>
                <div style="border-left: 4px solid #007bff; padding-left: 15px; margin-top: 10px; color: #444;">
                    {message}
                </div>
                <br>
                <p style="font-size: 12px; color: #aaa;">This message was sent via studymate's contact form.</p>
            </div>
            """

            text_content = strip_tags(html_content)

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email,
                reply_to=[email]
            )
            email_msg.attach_alternative(html_content, "text/html")
            email_msg.send(fail_silently=False)

            messages.success(request, "Email Sent | Your email has been sent successfully!")
            return redirect('home')

        else:
            messages.warning(request, "Terms and Conditions Reminder | Please accept the terms and conditions to proceed.")

    return HttpResponse('Failed to send email')
