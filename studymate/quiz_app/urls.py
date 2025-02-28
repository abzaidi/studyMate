from django.contrib import admin
from django.urls import path
from quiz_app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("features/", views.features, name="features"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.loginPage, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.registerPage, name="register"),
    path("main/", views.main, name="main"),
    path("uploaded_content/", views.user_extracted_texts, name="uploaded_content"),
    path('send_email/', views.send_email, name='send_email'),
    path('redirect-to-register/', views.redirect_to_register, name='redirect_to_register'),
]
