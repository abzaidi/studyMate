from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("This is the home page!!")


def loginPage(request):
    return HttpResponse("This is the login page!!")


def registerPage(request):
    return HttpResponse("This is the registration page!!")


def main(request):
    return render(request, 'main.html')
