from django.db import models
from django.contrib.auth.models import User

class FoodRecipe(models.Model):
    # Relationship with User model - Many-to-One
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', null=True, blank=True)
    
    # Fields for FoodRecipe
    food_name = models.CharField(max_length=255, null=True, blank=True)
    food_description = models.TextField(null=True, blank=True)
    food_image = models.ImageField(upload_to='food')

    def __str__(self):
        return self.food_name

class Profile(models.Model):
    # Relationship with User model - One-to-One
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Authentication token for account verification
    auth_token = models.CharField(max_length=100)
    
    # Flag to track if the user's account is verified
    is_verified = models.BooleanField(default=False)
    
    # Timestamp for when the profile was created
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Token for password reset
    forgot_password_token = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
