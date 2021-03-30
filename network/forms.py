# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
# from django.core.exceptions import ValidationError
from django import forms
from .models import User, UserProfile, Post



class UserProfileForm(forms.ModelForm):
   
    class Meta:
        model = UserProfile
        fields = ('first_name','last_name','picture')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control','placeholder':'Last Name'}),
            'picture': forms.URLInput(attrs={'class': 'form-control','placeholder':'Profile Picture URL','blank':'true'})
        }
        labels = {
            'first_name':'',
            'last_name':'',
            'picture':''
        }
    
    
    def clean_picture(self):
        url = self.cleaned_data['picture']
        if not url:
            url = UserProfile.DEFAULT_PIC
        return url

class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ('content',)
        widgets = {'content':forms.Textarea(attrs={
                'class':'form-control','rows':3, 'placeholder':"What's Happening?",'id':"content_field"}),
                }
        labels = {
            'content':''
        }

