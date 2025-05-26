from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from roothub_app.EmailBackEnd import EmailBackEnd
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.timezone import now
from .models import *
from datetime import datetime

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
            return render(request, 'index.html', {
                        "entered_data": request.POST
                    })
        
def doLogout(request):
    logout(request)
    messages.success(request, "Logout Successful!")
    return redirect('/')

@login_required(login_url="/")
def profile_update(request):
    trainee_content = None
    trainer_content = None

    total_trainer = Trainers.objects.all().count()
    total_trainee = Trainee.objects.all().count()
    total_courses =Courses.objects.all().count()

    user = request.user.user_type

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
        # print(courses_for_trainer)
        trainer_content = {
            "courses_for_trainer":course,
            "user_all":trainer,  
            "experience":experience,
        }

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
        "ABOUT_SCHOOL":ABOUT_SCHOOL
    }
    return render(request, "profile.html",both)
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

# def get_monthly_data(request):
#     # Group trainers by month
#     trainer_data = Trainers.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Count('id')).order_by('month')

#     # Group trainees by month
#     trainee_data = Trainee.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Count('id')).order_by('month')

#     # Format the data for ApexCharts
#     months = []
#     trainer_totals = []
#     trainee_totals = []

#     # Combine data for trainers and trainees
#     for trainer in trainer_data:
#         month = trainer['month'].strftime('%B %Y')  # Format month as "Month Year"
#         months.append(month)
#         trainer_totals.append(trainer['total'])

#     for trainee in trainee_data:
#         trainee_totals.append(trainee['total'])

#     return JsonResponse({
#         'months': months,
#         'trainer_totals': trainer_totals,
#         'trainee_totals': trainee_totals,
#     })
def view_annoucements(request):
    announcement = Announcement.objects.filter()

    content = {
        "announcements":announcement
    }
    return render(request, "view_announcement.html", content)