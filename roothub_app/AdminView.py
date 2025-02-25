from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *

@login_required(login_url="/")
def home(request):
    return render(request, "admin_template/home.html")

@login_required(login_url="/")
def add_trainer(request):
    return render(request, "admin_template/add_trainer.html")

@login_required(login_url="/")
def add_trainer_save(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name").capitalize()
            middle_name = request.POST.get("middle_name").capitalize()
            last_name = request.POST.get("last_name").capitalize()
            gender = request.POST.get("gender")
            phone  = request.POST.get("phone")
            religion = request.POST.get("religion")
            experience = request.POST.get("experience")
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')
            username = request.POST.get("username")
            email = request.POST.get("email").lower().replace(' ', '')
            password = request.POST.get("password1")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            
            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, "Email already exists!")
                return redirect("add_trainer")
            
            elif gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return redirect('add_trainer')
            
            elif len(password) < 11:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("add_trainer")

            elif 11>len(phone)>15:
                messages.error(request,"Input an appropiate phone number")
                return redirect("add_trainer")
            
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("add_trainer")
            
            else:
                user = CustomUser.objects.create_user(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    username=username,
                    profile_pic=profile_pic,
                    user_type=2
                )
                user.save()
                
                trainer = user.trainers 
                trainer.gender = gender
                trainer.address = address
                trainer.religion = religion
                trainer.state = state
                trainer.city = city
                trainer.experience = experience
                trainer.country = country
                trainer.phone = phone
                trainer.save()

                messages.success(request, "Trainer Added Successfully")
                return redirect("add_trainer")

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainer")

@login_required(login_url="/")
def view_trainer(request):
    trainers = Trainers.objects.all()
    total_trainees = trainers.count()
    context = {
        'trainers': trainers,
        'total_trainers': total_trainees,
    }
    return render(request, "admin_template/view_trainer.html", context)

@login_required(login_url="/")
def add_trainee(request):
    return render(request, "admin_template/add_trainee.html")

@login_required(login_url="/")
def add_trainee_save(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name").capitalize()
            middle_name = request.POST.get("middle_name").capitalize()
            last_name = request.POST.get("last_name").capitalize()
            gender = request.POST.get("gender")
            phone  = request.POST.get("phone")
            religion = request.POST.get("religion")
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')
            username = request.POST.get("username")
            email = request.POST.get("email").lower().replace(' ', '')
            password = request.POST.get("password1")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            course_choice = request.POST.get("course")

            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, "Email already exists!")
                return redirect("add_trainee")
            
            elif gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return redirect('add_trainee')
            
            elif len(password) < 11:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("add_trainee")

            elif 11>len(phone)>15:
                messages.error(request,"Input an appropiate phone number")
                return redirect("ädd_trainee")
            
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("add_trainee")
            
            else:
                user = CustomUser.objects.create_user(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                    username=username,
                    profile_pic=profile_pic,
                    user_type=3
                )
                
                trainees = user.trainee
                trainees.gender = gender
                trainees.address = address
                trainees.religion = religion
                trainees.state = state
                trainees.city = city
                trainees.country = country
                trainees.phone = phone

                selected_course = Courses.objects.get(id=course_choice)
                trainees.course_id = selected_course 
                trainees.save()
                user.save()

                messages.success(request, "Trainee Added Successfully")
                return redirect("add_trainee")

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainee")
    else:
        return HttpResponse("This is showing because this request is not on Post. Try going back or refresh this page")

@login_required(login_url="/")
def view_trainee(request):
    trainees = Trainee.objects.all()
    total_trainees = trainees.count()
    context = {
        'trainees': trainees,
        'total_trainees': total_trainees,
    }
    return render(request, 'admin_template/view_trainee.html', context)

@login_required(login_url="/")
def assign_trainer(request):
    return render(request, "admin_template/assign_trainer.html")