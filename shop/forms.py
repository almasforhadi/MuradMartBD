from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 

from .models import Rating, Order

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']
        widgets = {
            'rating' : forms.Select(choices=[(i,i) for i in range(1,6)]),
            'comment' : forms.Textarea(attrs={'rows' : 4})
        }

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order 
        # Fixed: Added 'phone' field that was missing in the Order model
        fields = ['username', 'phone', 'address', 'note']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number', 'type': 'tel'}),
            'note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add any special instructions...'}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }




from django import forms
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']