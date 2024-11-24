from django.contrib import admin
from django.urls import path
from quiz_app import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerPage, name="register"),
    path("main/", views.main, name="main"),
]
