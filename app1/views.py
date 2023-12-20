# Import necessary modules and classes
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import FoodRecipe, Profile
import uuid
from django.conf import settings
from django.core.mail import send_mail

# Decorator to ensure the user is logged in
@login_required
def food(request):
    """
    Handles the creation of a new food recipe by the logged-in user.
    """
    if request.method == "POST":
        # Get form data
        food_name = request.POST.get('food_name')
        food_description = request.POST.get('food_description')
        food_image = request.FILES.get('food_image')

        # Get the logged-in user
        user = request.user

        # Create a FoodRecipe object associated with the logged-in user
        food = FoodRecipe.objects.create(
            food_name=food_name, food_description=food_description, food_image=food_image, user=user
        )

        messages.success(request, f"{food.food_name} recipe created")

        return redirect('/')

    # Fetch only the recipes associated with the logged-in user
    food_recipes = FoodRecipe.objects.filter(user=request.user)
    return render(request, "food.html", {'food_recipes': food_recipes})

@login_required
def recipe(request):
    """
    Displays the list of recipes associated with the logged-in user.
    """
    message2 = 'tere jai ho bhai '
    # Fetch only the recipes associated with the logged-in user
    food_recipes = FoodRecipe.objects.filter(user=request.user)
    return render(request, "recipe.html", {'food_recipes': food_recipes, 'message2': message2})

@login_required
def delete_recipe(request, id):
    """
    Deletes a recipe owned by the logged-in user.
    """
    # Ensure that the logged-in user owns the recipe before deleting
    delete = FoodRecipe.objects.get(id=id, user=request.user)
    delete.delete()
    return redirect('/')

@login_required
def update_recipe(request, id):
    """
    Updates a recipe owned by the logged-in user.
    """
    update = FoodRecipe.objects.get(id=id, user=request.user)
    food = FoodRecipe.objects.filter(user=request.user)

    if request.method == "POST":
        # Get form data for updating the recipe
        food_name = request.POST.get('food_name')
        food_description = request.POST.get('food_description')
        food_image = request.FILES.get('food_image')

        # Update the recipe
        update.food_name = food_name
        update.food_description = food_description

        if food_image:
            update.food_image = food_image

        update.save()
        messages.success(request, f"{food_name} update recipe")
        return redirect('/')

    return render(request, 'update.html', {'food': update})

@login_required
def search(request):
    """
    Searches for recipes based on the provided query.
    """
    query = request.GET['search']
    # Fetch only the recipes associated with the logged-in user
    query_result = FoodRecipe.objects.filter(food_name__icontains=query, user=request.user).order_by('id')

    return render(request, 'search.html', {'query_result': query_result})

# Authentication views

def register(request):
    """
    Handles user registration.
    """
    if request.method == "POST":
        # Get user registration details from the form
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        try:
            # Validate and create a new user
            if password != confirmPassword:
                messages.warning(request, "Your Password is not the same, please check.")
                return HttpResponseRedirect(request.path_info)

            if User.objects.filter(username=username).first():
                messages.warning(request, "Username is already taken.")
                return HttpResponseRedirect(request.path_info)

            if User.objects.filter(email=email).first():
                messages.warning(request, "Email is already taken.")
                return HttpResponseRedirect(request.path_info)

            user_obj = User.objects.create_user(username=username, email=email, password=password)
            user_obj.first_name = firstName
            user_obj.last_name = lastName
            user_obj.save()

            # Generate an authentication token for email verification
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
            profile_obj.save()

            # Send email for account verification
            send_mail_after_registration(email, auth_token)
            messages.success(request, "Please verify your account. We have sent an email.")
            return redirect('login')

        except Exception as e:
            print(e)

    return render(request, 'register.html')

def send_mail_after_registration(email, token):
    """
    Sends an email to the user with an account verification link.
    """
    subject = 'Your Account needs to be verified'
    # message = f'Hi, click on the link to verify your account: http://127.0.0.1:8000/verify/{token}'
    message = f'Hi, click on the link to verify your account: https://crud-with-auth.onrender.com/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def verify(request, auth_token):
    """
    Handles account verification based on the received authentication token.
    """
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, "Your account is already verified.")
                return redirect('login')
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, "Your account has been verified.")
            return redirect('login')
        else:
            messages.success(request, "Error")
    except Exception as e:
        print(e)
        return render(request, 'login.html')

def user_login(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username).first()

        if user_obj is None:
            messages.success(request, "User not found")
            return redirect('login')

        profile_obj = Profile.objects.filter(user=user_obj).first()

        if not profile_obj.is_verified:
            messages.success(request, "Profile is not verified. Please check your email.")
            return redirect('login')

        user_obj = authenticate(username=username, password=password)

        if user_obj is not None:
            login(request, user_obj)
            messages.success(request, f"Welcome, you are now logged in.")
            return redirect('/')
        else:
            messages.warning(request, "Wrong details")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request):
    """
    Logs out the currently logged-in user.
    """
    logout(request)
    return redirect('login')

def forgot_password(request):
    """
    Handles the request for password reset.
    """
    try:
        if request.method == "POST":
            username = request.POST.get('username')

            if not User.objects.filter(username=username).first():
                messages.success(request, "No user found with this username.")
                return redirect('forgot_password')

            user_obj = User.objects.get(username=username)
            token = str(uuid.uuid4())
            profile_obj = Profile.objects.get(user=user_obj)
            profile_obj.forgot_password_token = token
            profile_obj.save()
            send_forgot_mail(user_obj.email, token)
            messages.success(request, "An email has been sent.")
            return redirect('change_password')

    except Exception as e:
        print(e)

    return render(request, 'forgot_password.html')

def send_forgot_mail(email, token):
    """
    Sends an email with a link for password reset.
    """
    subject = 'Your forget password link'
    # message = f'Hi, click on the link to reset your password: http://127.0.0.1:8000/change_password/{token}'
    message = f'Hi, click on the link to reset your password: https://crud-with-auth.onrender.com/change_password/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True

def change_password(request, token):
    """
    Handles the password change process after a user requests a password reset.
    """
    context = {}
    try:
        profile_obj = Profile.objects.filter(forgot_password_token=token).first()

        if request.method == "POST":
            newPassword = request.POST.get('newPassword')
            confirmPassword = request.POST.get('confirmPassword')
            user_id = request.POST.get('user_id')
            context = {'user_id': profile_obj.user.id}

            if user_id is None:
                messages.success(request, 'User not found')
                return redirect(f'/change_password/{token}')

            if newPassword != confirmPassword:
                messages.success(request, 'Both passwords should be equal')
                return redirect(f'/change_password/{token}')

            user_obj = User.objects.get(id=user_id)
            user_obj.set_password(newPassword)
            user_obj.save()

            messages.success(request, 'Your password has been changed. You can now log in.')
            return redirect('login')

    except Exception as e:
        print(e)

    return render(request, 'change_password.html', context)
