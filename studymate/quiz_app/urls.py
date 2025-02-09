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
]
