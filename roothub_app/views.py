from django.http import HttpResponse
from django.shortcuts import render,redirect
from roothub_app.EmailBackEnd import EmailBackEnd
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import *

# Create your views here.

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT

schoolname=settings.SCHOOL_NAME


def login_view(request):
    return render(request, "index.html")

def dologin (request):
    if request.method!="POST":
        return HttpResponse("""<h2>Method not allowed</h2>
                            <p>Try reloading the page</p>
                            <br>Why you are seeing this is because your submision is not POST</br> """)
    else:
        emails = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')
        if "@" in emails:
            user=EmailBackEnd.authenticate(request, username=emails,password=password)
        else:
            user = authenticate(request, username=emails, password=password)
        if user!=None:
            login(request, user)
            if user.user_type == "1":
                messages.success(request, "Login Successful")
                return redirect("admin_home")
            elif user.user_type == "2":
                messages.success(request, "Login Successful")
                return redirect("trainer_home")
            else:
                messages.success(request, "Login Successful")
                return redirect("trainee_home")
        else:
            messages.error(request, "Invalid Login Details")
            return redirect("/")
        
def doLogout(request):
    logout(request)
    messages.success(request, "Logout Successful!")
    return redirect('/')

@login_required(login_url="/")
def profile_update(request):
    return render(request, "profile.html")