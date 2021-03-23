from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import RegisterForm

# Create your views here.
def register(response):
	if response.method == "POST":
		form = RegisterForm(response.POST)
		if form.is_valid():
			form.save()
			return redirect("/login/")
	else:
		form = RegisterForm()
	return render(response, "register/register.html", {"form":form})

def login_view(request):
	if request.method=='POST':
		form = AuthenticationForm(data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			return redirect('/')
	else:
		form = AuthenticationForm()
	return render(request, 'register/login.html', {"form":form})