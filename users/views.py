from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django import forms
from .models import UserProfile
from django.shortcuts import render, redirect
from django.contrib import messages

SECURITY_QUESTIONS = {
    "q1": "What is your favorite color?",
    "q2": "What is your first pet’s name?",
    "q3": "What is your mother's maiden name?"
}
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    security_answer = forms.CharField(max_length = 150,required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "security_answer"]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        validate_password(password1)  # Django built in
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please use a different one.")
        return email


    def save(self, commit=True):
        user = super().save(commit=False)
        # user.set_password(self.cleaned_data["password1"])  # Hash password
        if commit:
            user.save()
            # Create and link UserProfile with security question & answer
            UserProfile.objects.create(
                user=user,
                security_answer=self.cleaned_data["security_answer"].lower(),  # Normalize for case-insensitivity
            )

        return user


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next", 'home:index'))
    else:
        form = AuthenticationForm()
    return render(request, "users/login.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect('home:index')  

def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home:index')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, "users/signup.html", {"form": form})

class SecurityQuestionForm(forms.Form):
    username = forms.CharField(label="Username", max_length=150)
    answer = forms.CharField(label="Answer", max_length=150)

def forgot_password_view(request):
    if request.method == "POST":
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            user_answer = form.cleaned_data["answer"].lower()  # normalize case

            try:
                user = User.objects.get(username=username)
                # Access the user’s stored answer (already stored in lowercase)
                stored_answer = user.profile.security_answer

                if stored_answer == user_answer:
                    # Store username in session so password_reset_confirm_view knows which user
                    request.session["reset_user"] = user.username
                    return redirect("users:password_reset_confirm")  # Name of your URL pattern
                else:
                    messages.error(request, "Incorrect answer. Please try again.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = SecurityQuestionForm()

    return render(request, "users/password_reset.html", {"form": form})

def password_reset_confirm_view(request):
    username = request.session.get("reset_user")
    if not username:
        # If someone hits this URL directly or session expired, go back to the forgot flow
        return redirect("users:forgot_password")

    User = get_user_model()
    user = User.objects.get(username=username)

    if request.method == "POST":
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been successfully reset.")
            # Clear from session so the user can’t reset again without going through the flow
            del request.session["reset_user"]
            return redirect("users:login")
    else:
        form = SetPasswordForm(user)

    return render(request, "users/password_reset_confirm.html", {"form": form})
