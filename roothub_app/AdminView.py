from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.core.paginator import Paginator

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
                user.save()

                messages.success(request, "Trainer Added Successfully")
                return redirect("add_trainer")

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainer")

@login_required(login_url="/")
def view_trainer(request):
    trainers_list = Trainers.objects.all()
    paginator = Paginator(trainers_list, 10)  # Show 10 trainers per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_trainers': paginator.count,
    }
    return render(request, 'admin_template/view_trainer.html', context)

@login_required(login_url="/")
def add_trainee(request):
    courses = Courses.objects.all()
    context = {
        "courses":courses
    }
    return render(request, "admin_template/add_trainee.html", context)

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
                try:
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
                except Exception as e:
                    print(e)
                    messages.error(request, "An error saving the Custom User occured")
                    redirect("add_trainee")
                try:
                    trainees = user.trainee
                    trainees.gender = gender
                    trainees.address = address
                    trainees.religion = religion
                    trainees.state = state
                    trainees.city = city
                    trainees.country = country
                    trainees.phone = phone
                except Exception as ex:
                    print(ex)
                    messages.error(request, "An error saving the Trainee details occured")
                    redirect("add_trainee")
                try:
                    selected_course = Courses.objects.get(id=course_choice)
                    trainees.course_id = selected_course 
                    trainees.save()
                    user.save()
                except Exception as ex:
                    print(ex)
                    messages.error(request, "An error saving the Course occured")
                    redirect("add_trainee")
                    
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
    trainees_list = Trainee.objects.all()
    paginator = Paginator(trainees_list, 10)  # Show 10 trainees per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_trainees': paginator.count,
    }
    return render(request, 'admin_template/view_trainee.html', context)

@login_required(login_url="/")
def add_course(request):
    return render(request, "admin_template/add_course.html")

@login_required(login_url="/")
def add_course_save(request):
    if request.method == "POST":
        try:
            course_name = request.POST.get("course")
            price = request.POST.get("price","").strip()

            if not course_name:
                messages.error(request, "Course name cannot be empty.")
                return redirect("add_course")

            elif not price:
                messages.error(request, "Price cannot be empty.")
                return redirect("add_course")

            elif len(course_name) > 255:
                messages.error(request, "Course name is too long. Maximum length is 255 characters.")
                return redirect("add_course")
        
            elif Courses.objects.filter(course_name__iexact=course_name).exists():
                messages.error(request, f"The course '{course_name}' already exists.")
                return redirect("add_course")

            try:
                price_value = float(price)
                if price_value <= 0:
                    messages.error(request, "Price must be a positive number.")
                    return redirect("add_course")
            except ValueError as ve:
                print(ve)
                messages.error(request, "The was an error for the Value Error")
                return redirect("add_course")
            except Exception as e:
                print(e)
                messages.error(request, "An Unexpeted Error Occured")
                return redirect("add_course")

            else:
                try:
                    new_course = Courses.objects.create(course_name=course_name , price_name=price_value)
                    new_course.save()
                    messages.success(request, f"The Course: '{course_name}' has been added successfully with its corresponding price '{price}'!")
                    return redirect("add_course") 
            
                except Exception as ex:
                    # Catch any unexpected database or system errors
                    print(ex)
                    messages.error(request, f"An error occurred while adding the course and price")
                    return redirect("add_course")
        except Exception as e:
            print(e)
            messages.error(request, f"An error occurred")
            return redirect("add_course")

@login_required(login_url="/")
def view_course(request):
    courses = Courses.objects.all()
    total_course = courses.count()
    context = {
        "total_course":total_course,
        "courses":courses,
    }
    return render(request, "admin_template/view_course.html", context)

@login_required(login_url="/")
def assign_trainer(request):
    courses = Courses.objects.all()
    trainers = Trainers.objects.all()

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        trainer_id = request.POST.get('trainer_id')

        course = get_object_or_404(Courses, id=course_id)
        trainer = get_object_or_404(Trainers, id=trainer_id)

        if course.trainer_id:
            confirmation = request.POST.get('confirmation', 'no')
            if confirmation == 'yes':
                current_trainer = course.trainer_id
                course.trainer_id = trainer
                course.save()
                trainer.course_id.add(course)
                current_trainer.course_id.remove(course)

                messages.success(request, f" The Trainer '{trainer.trainer_name.first_name} {trainer.trainer_name.last_name}' has been assigned to the course {course.course_name}.")
            else:
                messages.error(request, "Trainer assignment was cancelled.")
        else:
            course.trainer_id = trainer
            course.save()
            trainer.course_id.add(course)

            messages.success(request, f" The Trainer '{trainer.trainer_name.first_name} {trainer.trainer_name.last_name}' has been assigned to the course {course.course_name}.")

        return redirect('assign_trainer')
    
    content = {
                'courses': courses,
               'trainers': trainers
        }

    return render(request, "admin_template/assign_trainer.html",content)

def get_current_trainer(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    if course.trainer_id:
        trainer_name = f"{course.trainer_id.trainer_name.first_name} {course.trainer_id.trainer_name.last_name}"
    else:
        trainer_name = None
    return JsonResponse({'trainer': trainer_name})

@login_required(login_url="/")
def edit_trainer(request,trainer):
    user = get_object_or_404(CustomUser, username=trainer)
    trainers = get_object_or_404(Trainers, trainer_name=user)

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
                user.save()

                messages.success(request, "Trainer Added Successfully")
                return redirect("add_trainer")

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainer")
    
    content = {
        "trainer":trainers,
    }
    return render(request, "admin_template/edit_trainer.html", content)

@login_required(login_url="/")
def edit_trainee(request,trainee):
    user = get_object_or_404(CustomUser, username=trainee)
    trainees = get_object_or_404(Trainee, trainee_name=user)
    course = Courses.objects.all()
    
    if request.method == "POST":
        pass

    content = {
        "trainee":trainees,
        "courses":course,
    }
    return render(request, "admin_template/edit_trainee.html", content)