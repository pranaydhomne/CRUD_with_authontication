from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app1.views import *

urlpatterns = [
    # Home page, mapped to the 'food' view
    path("", food, name='food'),

    # User registration
    path("accounts/register/", register, name='register'),

    # User login
    path("accounts/login/", user_login, name='login'),

    # Account verification
    path("verify/<auth_token>", verify, name='verify'),

    # User logout
    path('logout/', logout_view, name='logout_view'),

    # Forgot password
    path('forgot_password/', forgot_password, name='forgot_password'),

    # Password change with token
    path('change_password/<token>', change_password, name='change_password'),

    # Recipe deletion
    path('delete_recipe/<id>/', delete_recipe, name="delete_recipe"),

    # Recipe listing
    path("recipes/", recipe, name='recipes'),

    # Recipe update
    path('update_recipe/<int:id>/', update_recipe, name="update_recipe"),

    # Recipe search
    path('search/', search, name="search"),
]

# Serving static files during development
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
