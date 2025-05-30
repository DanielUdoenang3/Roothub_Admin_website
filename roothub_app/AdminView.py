from email.message import EmailMessage
import smtplib
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
# from django.db.models import F, FloatField, ExpressionWrapper
# from .forms import SendAnnouncement
# from django.views.generic import CreateView
from django.db.models import Q
from django.core.paginator import Paginator
from django.db.models import Count

EMAIL_HOST_USER = settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings.EMAIL_HOST
EMAIL_PORT = settings.EMAIL_PORT

schoolname=settings.SCHOOL_NAME
SCHOOL_SLOGAN=settings.SCHOOL_SLOGAN
SCHOOL_LOCATION=settings.SCHOOL_LOCATION
SCHOOL_NUM1=settings.SCHOOL_NUM1
SCHOOL_NUM2 = settings.SCHOOL_NUM2
SCHOOL_WEB=settings.SCHOOL_WEB
ABOUT_SCHOOL=settings.ABOUT_SCHOOL

@login_required(login_url="/")
def home(request):
    trainer = Trainers.objects.all().count()
    trainee = Trainee.objects.all().count()
    courses =Courses.objects.all().count()

    dates = Presentation.objects.values_list('date', flat=True).distinct()

    # selected_date = request.GET.get('date')
    # presentations = []
    # available_dates = Presentation.objects.dates('date', 'day')  # Distinct presentation dates

    # if selected_date:
    #     # Annotate and sort by calculated percentage
    #     percentage_expr = ExpressionWrapper(
    #         (F('score_appearance') + F('score_content')) * 5.0,
    #         output_field=FloatField()
    #     )

    #     presentations = Presentation.objects.filter(date=selected_date).annotate(
    #         percentage=percentage_expr
    #     ).order_by('-percentage')

    content = {

        "trainers":trainer,
        "trainees":trainee,
        "courses":courses,
        "dates":dates,
        # 'presentations': presentations,
        # 'date': selected_date,
        # 'available_dates': available_dates,
    }
    return render(request, "admin_template/home.html",content)

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
            username = request.POST.get("username").lower().strip()
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
            
            elif len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("add_trainer")

            elif 11>len(phone)>14:
                messages.error(request,"Input an appropiate phone number")
                return redirect("add_trainer")
            
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("add_trainer")
            
            else:
                email_sent = False
                if email:
                    try:
                        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        msg = EmailMessage()
                        msg['Subject'] = f"Welcome to {schoolname}"
                        msg['From'] = EMAIL_HOST_USER
                        msg['To'] = email
                        
                        msg.add_alternative(
                            f"""
                            <html>
                            <body>
                                <h2 style="color: #2E86C1;">Welcome to {schoolname}!</h2>
                                <p>Dear <strong>{str(first_name).capitalize()} {str(middle_name).capitalize()} {str(last_name).capitalize()}</strong>,</p>
                                <p>
                                    We are delighted to welcome you to {schoolname}! As a valued member of our community, you play a crucial role in our mission to provide an exceptional learning environment.
                                </p>
                                <p>
                                    Here at the {schoolname}, we are committed to supporting you and ensuring your experience with us is both rewarding and fulfilling.
                                </p>
                                <h3 style="margin-top: 20px; text-align:center;">Your Log In Credentials</h3>
                                <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                <p><strong>Username:</strong> {str(username).capitalize()}</p>
                                <p><strong>Email:</strong> {str(email).capitalize()}</p>
                                <p><strong>Password:</strong> {str(password)}</p>
                                <p>Access your dashboard at: <a href="https://roothub-admin-website.onrender.com/" target="_blank">RootHub-Admin-Webiste</a></p>
                                <p style="margin-top: 20px;">Best regards,</p>
                                <p><strong>{schoolname} Management</strong></p>
                            </body>
                            </html>
                            """,
                            subtype='html'
                        )
                        smtp.send_message(msg)
                        smtp.quit()
                        email_sent = True
                    except Exception as e:
                        print(e)
                        messages.error(request, f"Please check your internet connection!")
                        return render(request, "admin_template/add_trainer.html")
                    
                    if email_sent or (not email):
                
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

# @login_required(login_url="/")
# def add_trainer_save(request):
#     if request.method == "POST":
#         try:
#             first_name = request.POST.get("first_name").capitalize()
#             middle_name = request.POST.get("middle_name").capitalize()
#             last_name = request.POST.get("last_name").capitalize()
#             gender = request.POST.get("gender")
#             phone  = request.POST.get("phone")
#             religion = request.POST.get("religion")
#             experience = request.POST.get("experience")
#             profile_pic = request.FILES.get('profile_pic', 'blank.webp')
#             username = request.POST.get("username").lower().strip()
#             email = request.POST.get("email").lower().replace(' ', '')
#             password = request.POST.get("password1")
#             address = request.POST.get("address")
#             city = request.POST.get("city")
#             state = request.POST.get("state")
#             country = request.POST.get("country")
            
#             if CustomUser.objects.filter(email__iexact=email).exists():
#                 messages.error(request, "Email already exists!")
#                 return redirect("add_trainer")
            
#             elif gender == "Select Gender":
#                 messages.error(request, "Select Student Gender!")
#                 return redirect('add_trainer')
            
#             elif len(password) < 8:
#                 messages.error(request, "Password must be at least 8 characters long.")
#                 return redirect("add_trainer")

#             elif 11>len(phone)>14:
#                 messages.error(request,"Input an appropiate phone number")
#                 return redirect("add_trainer")
            
#             elif CustomUser.objects.filter(username__iexact=username).exists():
#                 messages.error(request, "Username already exists!")
#                 return redirect("add_trainer")
            
#             else:
#                 user = CustomUser.objects.create_user(
#                     first_name=first_name,
#                     middle_name=middle_name,
#                     last_name=last_name,
#                     email=email,
#                     password=password,
#                     username=username,
#                     profile_pic=profile_pic,
#                     user_type=2
#                 )
                
                
#                 trainer = user.trainers
#                 trainer.gender = gender
#                 trainer.address = address
#                 trainer.religion = religion
#                 trainer.state = state
#                 trainer.city = city
#                 trainer.experience = experience
#                 trainer.country = country
#                 trainer.phone = phone
#                 trainer.save()
#                 user.save()

#                 messages.success(request, "Trainer Added Successfully")
#                 return redirect("add_trainer")

#         except Exception as excepts:
#             print(excepts)
#             messages.error(request, "An Unexcepted error occured")
#             return redirect("add_trainer")

@login_required(login_url="/")
def view_trainer(request):
    trainers_list = Trainers.objects.all().order_by('id')
    paginator = Paginator(trainers_list, 10)

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
            username = request.POST.get("username").lower().strip()
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
            
            elif len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("add_trainee")

            elif 11>len(phone)>15:
                messages.error(request,"Input an appropiate phone number")
                return redirect("add_trainee")
            
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("add_trainee")
            
            else:
                email_sent = False
                if email:
                    try:
                        smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
                        smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                        msg = EmailMessage()
                        msg['Subject'] = f"Welcome to {schoolname}"
                        msg['From'] = EMAIL_HOST_USER
                        msg['To'] = email
                        
                        msg.add_alternative(
                            f"""
                            <html>
                            <body>
                                <h2 style="color: #2E86C1;">Welcome to {schoolname}!</h2>
                                <p>Dear <strong>{str(first_name).capitalize()} {str(middle_name).capitalize()} {str(last_name).capitalize()}</strong>,</p>
                                <p>
                                    We are delighted to welcome you to {schoolname}! As a valued member of our community, you play a crucial role in our mission to provide an exceptional learning environment.
                                </p>
                                <p>
                                    Here at the {schoolname}, we are committed to supporting you and ensuring your experience with us is both rewarding and fulfilling.
                                </p>
                                <h3 style="margin-top: 20px; text-align:center;">Your Log In Credentials</h3>
                                <strong style="margin-top: 20px; color:red; text-align:center;">Please keep these credentials confidential!</strong>
                                <p><strong>Username:</strong> {str(username).capitalize()}</p>
                                <p><strong>Email:</strong> {str(email).capitalize()}</p>
                                <p><strong>Password:</strong> {str(password)}</p>
                                <p>Access your dashboard at: <a href="https://roothub-admin-website.onrender.com/" target="_blank">RootHub-Admin-Webiste</a></p>
                                <p style="margin-top: 20px;">Best regards,</p>
                                <p><strong>{schoolname}</strong></p>
                            </body>
                            </html>
                            """,
                            subtype='html'
                        )
                        smtp.send_message(msg)
                        smtp.quit()
                        email_sent = True
                    except:
                        messages.error(request, f"Please check your internet connection!")
                        return redirect("add_trainee")
                    if email_sent or (not email):
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
                            return redirect("add_trainee")
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
                            return redirect("add_trainee")
                        try:
                            selected_course = Courses.objects.get(id=course_choice)
                            trainees.course_id = selected_course 
                            trainees.save()
                            user.save()
                        except Exception as ex:
                            print(ex)
                            messages.error(request, "Select a course or you add Course")
                            return redirect("add_trainee")
                    
                messages.success(request, "Trainee Added Successfully")
                return redirect("add_trainee")
            
        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainee")
    else:
        return HttpResponse("This is showing because this request is not on Post. Try going back or refresh this page")

# @login_required(login_url="/")
# def add_trainee_save(request):
#     if request.method == "POST":
#         try:
#             first_name = request.POST.get("first_name").capitalize()
#             middle_name = request.POST.get("middle_name").capitalize()
#             last_name = request.POST.get("last_name").capitalize()
#             gender = request.POST.get("gender")
#             phone  = request.POST.get("phone")
#             religion = request.POST.get("religion")
#             profile_pic = request.FILES.get('profile_pic', 'blank.webp')
#             username = request.POST.get("username").lower().strip()
#             email = request.POST.get("email").lower().replace(' ', '')
#             password = request.POST.get("password1")
#             address = request.POST.get("address")
#             city = request.POST.get("city")
#             state = request.POST.get("state")
#             country = request.POST.get("country")
#             course_choice = request.POST.get("course")

#             if CustomUser.objects.filter(email__iexact=email).exists():
#                 messages.error(request, "Email already exists!")
#                 return redirect("add_trainee")
            
#             elif gender == "Select Gender":
#                 messages.error(request, "Select Student Gender!")
#                 return redirect('add_trainee')
            
#             elif len(password) < 8:
#                 messages.error(request, "Password must be at least 8 characters long.")
#                 return redirect("add_trainee")

#             elif 11>len(phone)>15:
#                 messages.error(request,"Input an appropiate phone number")
#                 return redirect("add_trainee")
            
#             elif CustomUser.objects.filter(username__iexact=username).exists():
#                 messages.error(request, "Username already exists!")
#                 return redirect("add_trainee")
            
#             else:
#                 try:
#                     user = CustomUser.objects.create_user(
#                         first_name=first_name,
#                         middle_name=middle_name,
#                         last_name=last_name,
#                         email=email,
#                         password=password,
#                         username=username,
#                         profile_pic=profile_pic,
#                         user_type=3
#                     )
#                 except Exception as e:
#                     print(e)
#                     messages.error(request, "An error saving the Custom User occured")
#                     return redirect("add_trainee")
#                 try:
#                     trainees = user.trainee
#                     trainees.gender = gender
#                     trainees.address = address
#                     trainees.religion = religion
#                     trainees.state = state
#                     trainees.city = city
#                     trainees.country = country
#                     trainees.phone = phone
#                 except Exception as ex:
#                     print(ex)
#                     messages.error(request, "An error saving the Trainee details occured")
#                     return redirect("add_trainee")
#                 try:
#                     selected_course = Courses.objects.get(id=course_choice)
#                     trainees.course_id = selected_course 
#                     trainees.save()
#                     user.save()
#                 except Exception as ex:
#                     print(ex)
#                     messages.error(request, "Select a course or you add Course")
#                     return redirect("add_trainee")
                    
#                 messages.success(request, "Trainee Added Successfully")
#                 return redirect("add_trainee")
            
#         except Exception as excepts:
#             print(excepts)
#             messages.error(request, "An Unexcepted error occured")
#             return redirect("add_trainee")
#     else:
#         return HttpResponse("This is showing because this request is not on Post. Try going back or refresh this page")

@login_required(login_url="/")
def view_trainee(request):
    trainees_list = Trainee.objects.all().order_by('id')
    paginator = Paginator(trainees_list, 10)

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
                    new_course = Courses.objects.create(course_name=course_name , price=price_value)
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
    courses_list = Courses.objects.annotate(num_trainees=Count('trainees')).order_by('id')
    paginator = Paginator(courses_list, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'total_course': paginator.count,
        'courses': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'admin_template/view_course.html', context)

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

@login_required(login_url="/")
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
            profile_pic = request.FILES.get('profile_pic')
            username = request.POST.get("username").strip().lower()
            email = request.POST.get("email").lower().replace(' ', '')
            password = request.POST.get("password1")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")

            if email != user.email:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return redirect("edit_trainer",trainer)
                else:
                    user.email = email
            
            elif gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return redirect("edit_trainer",trainer)
            
            if password:
                len(password) < 8
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("edit_trainer",trainer)

            elif 11>len(phone)>15:
                messages.error(request,"Input an appropiate phone number")
                return redirect("edit_trainer",trainer)
            
            if username != user.username:
                if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists!")
                    return redirect("edit_trainer",trainer)
                else:
                    user.username = username
            

            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if profile_pic:
                user.profile_pic = profile_pic
            else:
                user.profile_pic=user.profile_pic
            user.save()

            trainers.gender = gender
            trainers.address = address
            trainers.religion = religion
            trainers.state = state
            trainers.city = city
            trainers.experience=experience
            trainers.country = country
            trainers.phone = phone
            trainers.save()

            messages.success(request, "Trainer Edited Successfully")
            return redirect("edit_trainer",trainer)

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("edit_trainer",trainer)
    
    content = {
        "trainer":trainers,
    }
    return render(request, "admin_template/edit_trainer.html", content)

@login_required(login_url="/")
def edit_trainee(request, trainee):
    user = get_object_or_404(CustomUser, username=trainee)
    trainees = get_object_or_404(Trainee, trainee_name=user)
    courses = Courses.objects.all()

    try:
        if request.method == "POST":
            first_name = request.POST.get("first_name").capitalize()
            middle_name = request.POST.get("middle_name").capitalize()
            last_name = request.POST.get("last_name").capitalize()
            gender = request.POST.get("gender")
            phone = request.POST.get("phone")
            religion = request.POST.get("religion")
            profile_pic = request.FILES.get('profile_pic')
            username = request.POST.get("username").strip().lower()
            email = request.POST.get("email").lower().replace(' ', '')
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            course_choice = request.POST.get("course")

            if email != user.email:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return redirect("edit_trainer",trainee)
                else:
                    user.email = email

            elif gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return redirect("edit_trainee", trainee)

            elif len(phone) < 11 or len(phone) > 15:
                messages.error(request, "Input an appropriate phone number")
                return redirect("edit_trainee", trainee)

            if username != user.username:
                if CustomUser.objects.filter(username__iexact=username).exists():
                    messages.error(request, "Username already exists!")
                    return redirect("edit_trainer",trainee)
                else:
                    user.username = username

            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            user.email = email
            user.username = username
            if profile_pic:
                user.profile_pic = profile_pic
            else:
                user.profile_pic=user.profile_pic
            user.save()

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

            messages.success(request, "Trainee details updated successfully")
            return redirect("view_trainee")
    except Exception as e:
        print(e)
        messages.error(request, "An Unexcepted error occured")
        return redirect("edit_trainee", trainee)


    content = {
        "trainee": trainees,
        "courses": courses,
    }
    return render(request, "admin_template/edit_trainee.html", content)

@login_required(login_url="/")
def edit_course(request, course):
    courses = get_object_or_404(Courses, id=course)

    if request.method == "POST":
        course_name = request.POST.get("course")
        price = request.POST.get("price").strip()

        if not course_name:
            messages.error(request, "Course name cannot be empty.")
            return redirect("edit_course", course)

        if not price:
            messages.error(request, "Price cannot be empty.")
            return redirect("edit_course", course)

        try:
            price = float(price)
        except ValueError:
            messages.error(request, "Price must be a valid number.")
            return redirect("edit_course", course)

        if course_name != courses.course_name:
            if Courses.objects.filter(course_name__iexact=course_name).exists():
                messages.error(request, "Course already exists!")
                return redirect("edit_course", course)

        courses.course_name = course_name
        courses.price = price
        courses.save()

        messages.success(request, f"The course '{courses.course_name}' has been successfully updated to '{course_name}' with the price NGN{price}'")
        return redirect("view_course")

    context = {
        'courses': courses
    }
    return render(request, 'admin_template/edit_course.html', context)

@login_required(login_url="/")
def search(request):
    data=None
    try:
        if request.method == "POST":
            search = request.POST.get("search")
            if search:
                trainer_search = Trainers.objects.filter(
                    Q(trainer_name__username__icontains=search)|
                    Q(trainer_name__first_name__icontains=search)|
                    Q(trainer_name__middle_name__icontains=search)|
                    Q(trainer_name__last_name__icontains=search)|
                    Q(trainer_name__email__icontains=search)|
                    Q(phone__icontains=search)|
                    Q(state__icontains=search)|
                    Q(religion__icontains=search)|
                    Q(city__icontains=search)
                )
                trainee_search = Trainee.objects.filter(
                    Q(trainee_name__username__icontains=search)|
                    Q(trainee_name__first_name__icontains=search)|
                    Q(trainee_name__middle_name__icontains=search)|
                    Q(trainee_name__last_name__icontains=search)|
                    Q(trainee_name__email__icontains=search)|
                    Q(phone__icontains=search)|
                    Q(state__icontains=search)|
                    Q(religion__icontains=search)|
                    Q(city__icontains=search)
                )
                data = {
                    "trainers":trainer_search,
                    "trainees":trainee_search,
                    "param":search
                }
    except Exception as e:
        print(e)
        messages.error(request, f"An error was encountered {e}")
    return render(request, "admin_template/search.html", data)


@login_required(login_url="/")
def delete_trainer(request, trainer):
    try:
        user = get_object_or_404(CustomUser, username=trainer)
        trainer = get_object_or_404(Trainers, trainer_name=user)
        trainer_user = str(user)
        user.delete()
        trainer.delete()
        messages.success(request, f"Trainer{trainer_user.capitalize()} was deleted sucessfully")
    except Exception as e:
        print(e)
        messages.error(request, f"Trainer{trainer_user.capitalize()} was not deleted sucessfully")
    return redirect("view_trainer")

@login_required(login_url="/")
def delete_trainee(request, trainee):
    try:
        user = get_object_or_404(CustomUser, username=trainee)
        trainee = get_object_or_404(Trainee, trainee_name=user)
        trainee_user=str(user)
        user.delete()
        trainee.delete()
        messages.success(request, f"Trainee {trainee_user.capitalize()} was deleted sucessfully")
    except Exception as e:
        print(e)
        messages.error(request, f"Trainee {trainee_user.capitalize()} was not deleted sucessfully")
    return redirect("view_trainee")

@login_required(login_url="/")
def delete_course(request, course):
    try:
        course = get_object_or_404(Courses, course_name=course)
        course_name = str(course)
        course.delete()
        messages.success(request, f"The Course {course_name.capitalize()} was deleted sucessfully")
    except Exception as e:
        print(e)
        messages.error(request, f"The Course {course_name.capitalize()} was deleted unsuccessfully")
    return redirect("view_course")

@login_required(login_url="/")
def send_announcement(request):
    if request.method == "POST":
        try:
            title = request.POST.get("title")
            description = request.POST.get("description")
            file = request.FILES.get("file")

            Announcement.objects.create(
                title = title,
                description = description,
                file = file
            )
            messages.success(request, "Announcement sent successfully")
            
        except Exception as e:
            print(e)
            messages.error(request,f"Announcement not sent due to {e}")
    return render(request, "admin_template/send_announcement.html")

@login_required(login_url="/")
def view_announcement(request):
    announcements = Announcement.objects.all()

    return render(request, "admin_template/view_announcement.html",{
        "announcements":announcements,
    })

def edit_announcement(request, announcement_title):
    announcement = get_object_or_404(Announcement, title=announcement_title)
    try:
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            file = request.FILES.get("file")

            announcement.title = title
            announcement.description = description
            if file:
                announcement.file = file
            announcement.save()
            messages.success(request, "Announcement Updated suucessfully")
            return redirect("view_announcement")
    except Exception as e:
        print(e)
        messages.error(request, f"An error occured {e}")
    return render(request, "admin_template/edit_announcement.html", {"announcement":announcement})

@login_required(login_url="/")
def delete_announcement(request, announcement_title):
    try:
        announcement = Announcement.objects.filter(title=announcement_title)
        announcement.delete()
        messages.success(request, f"The announcement {announcement_title} has been deleted successfully")
    except Exception as e:
        print(e)
        messages.error(request, f"An error occured {e}")
    return redirect("view_announcement")

@login_required(login_url="/")
def trainee_details(request, username):
    user = get_object_or_404(CustomUser, username=username)
    trainee = get_object_or_404(Trainee, trainee_name=user)

    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    if password1 and password2:
        if password1 == password2:
            user.set_password(password2)
            user.save()
            messages.success(request, "User Password Changed successfully")
        else:
            messages.error(request, "The Passwords you entered are not matching")
    context={
        'user':user,
        'trainee':trainee,
    }

    return render(request, 'admin_template/view_trainee_details.html', context)

def trainer_details(request, username):
    user = get_object_or_404(CustomUser, username=username)
    trainer = get_object_or_404(Trainers, trainer_name=user)
    course = Courses.objects.filter(trainer_id=trainer)

    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    if password1 and password2:
        if password1 == password2:
            user.set_password(password2)
            user.save()
            messages.success(request, "User Password Changed successfully")
        else:
            messages.error(request, "The Passwords you entered are not matching")

    context={
        'user':user,
        'trainer':trainer,
        'course':course,
    }

    return render(request, 'admin_template/view_trainer_details.html', context)



# def star_trainees_view(request):
#     selected_date = request.GET.get('date')
#     # presentations = []
#     available_dates = Presentation.objects.dates('date', 'day')  # Distinct presentation dates

#     if selected_date:
#         # Annotate and sort by calculated percentage
#         percentage_expr = ExpressionWrapper(
#             (F('score_appearance') + F('score_content')) * 5.0,
#             output_field=FloatField()
#         )

#         presentations = Presentation.objects.filter(date=selected_date).annotate(
#             percentage=percentage_expr
#         ).order_by('-percentage')

#     return render(request, 'admin_template/home.html', {
#         'presentations': presentations,
#         'date': selected_date,
#         'available_dates': available_dates,
#     })


# def star_trainee_presenter(request):

# from django.urls import reverse_lazy

# class Send_Announcement(CreateView):
#     model = Announcement
#     form_class = SendAnnouncement
#     template_name = 'admin_template/send_announcement.html'
#     success_url = reverse_lazy('send_announcement')  # Use reverse_lazy for URL resolution

#     def form_valid(self, form):
#         self.object = form.save(commit=False)
#         self.object.user = self.request.user
#         self.object.save()
#         messages.success(self.request, "Announcement sent successfully!")
#         return super().form_valid(form)