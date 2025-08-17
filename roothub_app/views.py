from email.message import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from roothub_app.EmailBackEnd import EmailBackEnd
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from roothub_app.utils.token import create_access_token, decode_access_token
from .models import *
import smtplib
from datetime import datetime, timedelta
from roothub_app.backend.email_backend import send_forgot_password_email, send_login_body

# Create your views here.

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

def Announcement_View(request):
    announcements = Announcement.objects.all()
    return render(request, "base.html", {"announcements": announcements})

def login_view(request):
    return render(request, "index.html")

def dologin (request):
    if request.method!="POST":
        return HttpResponse("""<h2>Method not allowed</h2>
                            <p>Try reloading the page</p>
                            <br>Why you are seeing this is because your submision is not POST</br> """)
    if request.method == "POST":
        emails = request.POST.get('email', '').lower()
        password = request.POST.get('password', '')
        if "@" in emails:
            user=EmailBackEnd.authenticate(request, username=emails,password=password)
        else:
            user = authenticate(request, username=emails, password=password)
        if user!=None:
            if user.is_active == True:
                first_name = user.first_name.capitalize()
                last_name = user.last_name.capitalize()
                email = user.email

                send_login_body(first_name, last_name, schoolname, EMAIL_HOST_USER, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, email)

                login(request, user)
                if user.user_type == "1":
                    messages.success(request, "Login Successful")
                    return redirect("admin_home")
                elif user.user_type == "2":
                    messages.success(request, "Login Successful")
                    return redirect("trainer_home")
                elif user.user_type == "3":
                    messages.success(request, "Login Successful")
                    return redirect("trainee_home")
                else:
                    messages.error(request, "User type is not recognized.")
                    return render(request, 'index.html', {
                        "entered_data": request.POST
                    })
            else:
                messages.error(request, "Account is not active!")
                return render(request, 'index.html', {
                        "entered_data": request.POST
                    })
        else:
            if "@" in request.POST.get('email'):
                messages.error(request, "Email and password are invalid!")
                return render(request, 'index.html', {
                        "entered_data": request.POST
                    })
                
            else:
                email=request.POST.get('email')
                messages.error(request, "Username and password are invalid!")
                return render(request, 'index.html', {
                        "entered_data": request.POST
                    })
    else:    
        context={
            'email':email,
        }
        return render(request, 'index.html', context)
        
def doLogout(request):
    logout(request)
    messages.success(request, "Logout Successful!")
    return redirect('/')

@login_required(login_url="/")
def profile(request):
    try:
        trainee_content = None
        trainer_content = None
        admin_content = None
        total_trainer = None
        total_trainee = None
        total_courses = None

        user = request.user.user_type
        
        if user == "1":
            users = get_object_or_404(CustomUser, username=request.user)
            admin = get_object_or_404(Admin, admin_name=users)
            admin_content = {
                "admin":admin,
            }

        total_trainer = Trainers.objects.all().count()
        total_trainee = Trainee.objects.all().count()
        total_courses =Courses.objects.all().count()

        if user == "3":
            trainee = get_object_or_404(Trainee, trainee_name=request.user)
            course = get_object_or_404(Courses, trainees=trainee)
            trainee_content = {
                "total_course":total_courses,
                "total_trainer":total_trainer,
                "total_trainee":total_trainee,
                "courses_for_trainer":course,
                "user_all":trainee,
            }
            
        elif user == "2":
            trainer = Trainers.objects.get(trainer_name=request.user)
            courses = Courses.objects.filter(trainer_id=trainer).all()
            experience = trainer.experience

            course = []
            for coursess in courses:
                course.append({
                    "coursess":coursess
                })
            trainer_content = {
                "courses_for_trainer":course,
                "user_all":trainer,  
                "experience":experience,
            }
    except Exception as e:
        print(e)
    both = {
        "trainer_content":trainer_content,
        "trainee_content":trainee_content,
        "total_course":total_courses,
        "total_trainer":total_trainer,
        "total_trainee":total_trainee,
        "schoolname":schoolname,
        "SCHOOL_SLOGAN":SCHOOL_SLOGAN,
        "SCHOOL_LOCATION":SCHOOL_LOCATION,
        "SCHOOL_NUM1":SCHOOL_NUM1,
        "SCHOOL_NUM2":SCHOOL_NUM2,
        "SCHOOL_WEB":SCHOOL_WEB,
        "ABOUT_SCHOOL":ABOUT_SCHOOL,
        "admin_content":admin_content,
    }
    return render(request, "profile.html",both)

@login_required(login_url="/")
def profile_update(request, admin):
    if request.method == "POST":
        users = get_object_or_404(CustomUser, username=admin)
        admin = get_object_or_404(Admin, admin_name=users)

        # try:
        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        email = request.POST.get("email")
        profile_pic = request.FILES.get("profile_pic")
        password = request.POST.get("password")
        personal_info = request.POST.get("personal_info")

        if CustomUser.objects.filter(email__iexact=email).exclude(id=users.id).exists():
            messages.error(request, "Email already exists!")
            return redirect("profile")
        
        if password:
            if len(password) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                return redirect("profile")

        elif 11>len(phone)>15:
            messages.error(request,"Input an appropiate phone number")
            return redirect("profile")
        
        elif CustomUser.objects.filter(username__iexact=username).exclude(id=users.id).exists():
            messages.error(request, "Username already exists!")
            return redirect("profile")
        else:
            users.first_name = first_name
            users.middle_name = middle_name
            users.last_name = last_name
            users.email = email
            # users.username = username
            if password:
                users.set_password(password)
            if profile_pic:
                users.profile_pic = profile_pic
            users.save()

            admin.gender = gender
            admin.phone = phone
            admin.address = address
            admin.personal_info = personal_info
            admin.save()

            messages.success(request, "Your profile has been updated successfully")
            return redirect("profile")

        # except Exception as e:
        #     print(e)
        #     messages.error(request, "An Unexcepted error occured")
        #     return redirect("profile")


@login_required(login_url="/")
def get_unread_announcements(request):
    user = request.user
    unread_announcements = Announcement.objects.exclude(read_by=user).values(
        "id", "title", "description", "created_at"
    )
    unread_count = unread_announcements.count()

    return JsonResponse({"unread_count": unread_count, "unread_announcements": list(unread_announcements)})

def mark_announcement_as_read(request, announcement_id):
    user = request.user
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.read_by.add(user)
        return JsonResponse({"success": True})
    except Announcement.DoesNotExist:
        return JsonResponse({"success": False, "error": "Announcement not found."}, status=404)

@login_required(login_url="/")
def mark_attendance(request):
    courses = Courses.objects.all()
    try:
        if request.method == "POST":
            course_id = request.POST.get("course")
            date = request.POST.get("date")

            if not course_id or not date:
                content = {
                    "courses": courses,
                    "error": "Please select a course and date."
                }
                return render(request, "admin_template/mark_attendance.html", content)

            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                content = {
                    "courses": courses,
                    "error": "Please select a course and date."
                }
                return render(request, "admin_template/mark_attendance.html", content)

            course = get_object_or_404(Courses, id=course_id)
            attendance, created = Attendance.objects.get_or_create(
                course=course,
                attendance_date=date
            )

            present_ids = request.POST.getlist("present") 
            absent_ids = request.POST.getlist("absent")

            for trainee_id in present_ids:
                trainee = get_object_or_404(Trainee, id=trainee_id)
                AttendanceReport.objects.update_or_create(
                    attendance_id=attendance,
                    student_id=trainee,
                    status=True
                )

            # Process Absent trainees
            for trainee_id in absent_ids:
                trainee = get_object_or_404(Trainee, id=trainee_id)
                AttendanceReport.objects.update_or_create(
                    attendance_id=attendance,
                    student_id=trainee,
                    status=False
                )
            messages.success(request,"Attendance marked sucessfully")
            return redirect("view_attendance")
    except Exception as e:
        print(e)
    content = {
        "courses" : courses
    }
    return render(request, "admin_template/mark_attendance.html", content)

@login_required(login_url="/")
def get_trainees(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return JsonResponse({"error": "Course ID is required"}, status=400)

    try:
        course = Courses.objects.get(id=course_id)
    except Courses.DoesNotExist:
        return JsonResponse({"error": "Course not found"}, status=404)
    except Courses.MultipleObjectsReturned:
        return JsonResponse({"error": "Multiple courses found with the same ID"}, status=400)

    trainees = course.trainees.all()
    if not trainees.exists():
        return JsonResponse({"error": "No students found for this course"}, status=404)

    trainee_data = [
        {"id": trainee.id, "name": f"{trainee.trainee_name.first_name} {trainee.trainee_name.last_name}"}
        for trainee in trainees
    ]
    return JsonResponse({"trainees": trainee_data}, status=200)

def view_attendance(request):
    courses = Courses.objects.all()
    content = {
        "courses": courses,
    }
    return render(request, "admin_template/view_attendance.html", content)

@login_required(login_url="/")
def get_attendance_data(request, trainee_id):
    try:
        # Get the trainee and their registration date
        trainee = Trainee.objects.get(id=trainee_id)
        registration_date = trainee.created_at.date()  # Registration date
    except Trainee.DoesNotExist:
        return JsonResponse({"error": "Trainee not found"}, status=500)

    # Fetch attendance records
    attendance_records = AttendanceReport.objects.filter(
        student_id=trainee_id, 
        attendance_id__attendance_date__gte=registration_date
    ).select_related('attendance_id')

    if not attendance_records.exists():
        return JsonResponse({
            "trainee_name": f"{trainee.trainee_name.first_name} {trainee.trainee_name.last_name}",
            "dates": [],
            "status": [],
            "present_percentage": 0,
            "absent_percentage": 0,
            "message": "No attendance records found for this trainee."
        })

    # Prepare data
    result_dates = []
    result_status = []
    present_count = 0
    absent_count = 0

    for record in attendance_records:
        attendance_date = record.attendance_id.attendance_date
        status = record.status
        result_dates.append(attendance_date.strftime("%Y-%m-%d"))
        result_status.append(status)
        if status:
            present_count += 1
        else:
            absent_count += 1

    # Calculate percentages
    total_marked = present_count + absent_count
    present_percentage = round((present_count / total_marked) * 100, 2) if total_marked > 0 else 0
    absent_percentage = round((absent_count / total_marked) * 100, 2) if total_marked > 0 else 0

    # Return data
    return JsonResponse({
        "trainee_name": f"{trainee.trainee_name.first_name} {trainee.trainee_name.last_name}",
        "dates": result_dates,
        "status": result_status,
        "present_percentage": present_percentage,
        "absent_percentage": absent_percentage,
    })


@login_required(login_url="/")
def mark_presentation(request):
    # try:
    courses = Courses.objects.all()
    if request.method == "POST":
        course_id = request.POST.get("course")
        date = request.POST.get("date")
        title = request.POST.get("title")
        comment = request.POST.get("comment")
        trainee_id = request.POST.get("trainee")
        score_appearance = request.POST.get("score_appearance")
        score_content = request.POST.get("score_content")

        if not course_id or not date or not trainee_id or not score_appearance or not score_content or not title or not comment:
            messages.error(request, "All fields are required!")
            return redirect("mark_presentation")
        
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format!")
            return redirect("mark_presentation")
        
        course = get_object_or_404(Courses, id=course_id)
        trainee = get_object_or_404(Trainee, id=trainee_id)
        presentation,created = Presentation.objects.update_or_create(
            course=course, date=date, title=title, trainee=trainee, comment=comment,
            score_appearance = score_appearance,score_content = score_content
        )
        presentation_report  = Presentation_report.objects.get_or_create(
            trainee_id = trainee,
            presentation_id = presentation 
        )
        presentation.save()
        messages.success(request, "Presentation marked successfully!")
        return redirect("view_presentation")
    # except Exception as e:
    #     print(e)
    #     messages.error(request,"An error was encounted check the terminal")
    
    content = {
        "courses": courses
    }
    return render(request, "admin_template/mark_presentation.html", content)

@login_required(login_url="/")
def get_trainees_by_course(request, course_id):
    date = request.GET.get('date')
    trainees = Trainee.objects.filter(course_id=course_id)
    trainees_list = [{"id": trainee.id, "name": f"{trainee.trainee_name.first_name} {trainee.trainee_name.last_name}"} for trainee in trainees]
    return JsonResponse({"trainees": trainees_list})

@login_required(login_url="/")
def view_presentation(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, "admin_template/view_presentation.html", context)

@login_required(login_url="/")
def get_dates_by_trainee(request, trainee_id):
    dates = Presentation.objects.filter(trainee_id=trainee_id).values_list('date', flat=True).distinct()
    dates_list = [{"date": date} for date in dates]
    return JsonResponse({"dates": dates_list})

@login_required(login_url="/")
def get_presentations_by_date(request, trainee_id, date):
    presentations = Presentation.objects.filter(trainee_id=trainee_id, date=date).select_related('course', 'trainee')
    presentations_list = [
        {
            "course_name": presentation.course.course_name,
            "trainee_name": f"{presentation.trainee.trainee_name.first_name} {presentation.trainee.trainee_name.last_name}",
            "date": presentation.date,
            "title": presentation.title,
            "score_appearance": presentation.score_appearance,
            "score_content": presentation.score_content,
            "comment": presentation.comment,
            "total_score": presentation.score_appearance + presentation.score_content
        }
        for presentation in presentations
    ]
    return JsonResponse({"presentations": presentations_list})

def star_trainee_view(request, date):
    presentations = Presentation.objects.filter(date = date)
    presentations_list = [
        {
            "course_name": presentation.course.course_name,
            "trainee_name": f"{presentation.trainee.trainee_name.first_name} {presentation.trainee.trainee_name.last_name}",
            "date": presentation.date,
            "title": presentation.title,
            "score_appearance": presentation.score_appearance,
            "score_content": presentation.score_content,
            "comment": presentation.comment,
            "total_score": presentation.score_appearance + presentation.score_content,
            "percentage": ((presentation.score_appearance + presentation.score_content) / 20) * 100
        }
        for presentation in presentations
    ]
    return JsonResponse({"presentations": presentations_list})

def view_annoucements(request):
    announcement = Announcement.objects.filter()

    content = {
        "announcements":announcement
    }
    return render(request, "view_announcement.html", content)

def trainers_trainees_per_month(request):
    # Get last 6 months
    months = []
    now = datetime.now()
    for i in range(5, -1, -1):
        month = (now.replace(day=1) - timedelta(days=30*i)).strftime('%b %Y')
        months.append(month)

    # Aggregate trainers
    trainers = (
        Trainers.objects.annotate(month=TruncMonth('updated_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    # Aggregate trainees
    trainees = (
        Trainee.objects.annotate(month=TruncMonth('updated_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

    # Prepare data for chart
    month_labels = []
    trainer_counts = []
    trainee_counts = []
    for m in months:
        month_labels.append(m)
        # Find count for this month
        t_count = next((item['count'] for item in trainers if item['month'].strftime('%b %Y') == m), 0)
        tr_count = next((item['count'] for item in trainees if item['month'].strftime('%b %Y') == m), 0)
        trainer_counts.append(t_count)
        trainee_counts.append(tr_count)

    return JsonResponse({
        "months": month_labels,
        "trainers": trainer_counts,
        "trainees": trainee_counts,
    })

def male_female_number_of_trainees(request):
    data = (
        Trainee.objects.values('gender')
        .annotate(count=Count('id'))
    )
    # Default to 0 if not found
    male_count = next((item['count'] for item in data if item['gender'].lower() == 'male'), 0)
    female_count = next((item['count'] for item in data if item['gender'].lower() == 'female'), 0)
    return JsonResponse({
        "labels": ["Male", "Female"],
        "counts": [male_count, female_count]
    })

def male_female_number_of_trainers(request):
    data = (
        Trainers.objects.values('gender')
        .annotate(count=Count('id'))
    )
    # Default to 0 if not found
    male_count = next((item['count'] for item in data if item['gender'].lower() == 'male'), 0)
    female_count = next((item['count'] for item in data if item['gender'].lower() == 'female'), 0)
    return JsonResponse({
        "labels": ["Male", "Female"],
        "counts": [male_count, female_count]
    })

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            token = create_access_token(data={"email": email})
            send_forgot_password_email(token=token, email=email)
            messages.success(request, f"An email has been sent successfully to {email}")

    return render(request, "forgot-password.html")

def forgot_password_link(request, token):
    if token:
        payload = decode_access_token(token)
        email = payload.get("email")

        checked_email = CustomUser.objects.filter(email=email)
        # checked_email = get_object_or_404(CustomUser, email=email)

        if not checked_email:
            messages.error(request, "This email is not registered with us")
            return render(request, "forgot-password.html")
        
        if not email:
            print("No email has been recieved")

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 == password2:
            checked_email.set_password(password2)
            checked_email.save()
            messages.success(request, "Password reseted successfully you can now login")
            return render(request, "index.html")
        else:
            messages.error(request, "Password does not match")

    context = {"request" : request.POST}

    return render(request, "reset-password.html", context)