# forms.py
from django import forms

class SecurityQuestionForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    answer = forms.CharField(label="Answer", max_length=150)
