from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
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
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from roothub_app.backend.email_backend import send_add_trainee, send_add_trainer, send_assign_trainer, send_invite_link
from roothub_app.utils.token import create_access_token, decode_access_token

# Import payment views
from .payment_views import (
    payment, trainee_payment_details, process_trainee_payment, 
    process_trainee_payment_save, process_installment_payment,
    trainer_payment_details, process_trainer_payment, 
    process_trainer_payment_save, api_trainer_payments
)

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
ALOWED_HOST_ONLINE = settings.ALOWED_HOST_ONLINE

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
    skill_expertise = SkillExpertise.objects.prefetch_related('competent_skills').all()
    context = {
        'skill_expertise': skill_expertise
    }
    return render(request, "admin_template/add_trainer.html", context)

@login_required(login_url="/")
def add_trainer_save(request):
    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name").capitalize()
            middle_name = request.POST.get("middle_name").capitalize()
            last_name = request.POST.get("last_name").capitalize()
            gender = request.POST.get("gender")
            phone  = request.POST.get("phone")
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')
            username = request.POST.get("username").lower().strip()
            email = request.POST.get("email").lower().replace(' ', '')
            password = request.POST.get("password1")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            birthday = request.POST.get("birthday")
            
            # Get selected skill expertise and competent skills
            selected_skill_expertise = request.POST.getlist("skill_expertise")
            selected_competent_skills = request.POST.getlist("competent_skills")
            
            account_no = request.POST.get("account_no")
            bank = request.POST.get("bank")
            commission_rate = request.POST.get("commission_rate")
            
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
                trainer.state = state
                trainer.city = city
                trainer.country = country
                trainer.phone = phone
                trainer.account_no = account_no
                trainer.birthday = birthday
                trainer.bank = bank
                trainer.commission_rate = commission_rate
                trainer.save()
                
                # Set many-to-many relationships after saving the trainer
                if selected_skill_expertise:
                    skill_expertise_objects = SkillExpertise.objects.filter(id__in=selected_skill_expertise)
                    trainer.skill_expertise.set(skill_expertise_objects)
                
                if selected_competent_skills:
                    competent_skills_objects = CompetentSkill.objects.filter(id__in=selected_competent_skills)
                    trainer.competent_skills.set(competent_skills_objects)
                
                user.save()

                send_add_trainer(first_name, middle_name, last_name, username, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE, email)
                messages.success(request, "Trainer Added Successfully")
                return redirect("add_trainer")

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("add_trainer")


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
            category = request.POST.get("category")
            gender = request.POST.get("gender")
            phone  = request.POST.get("phone")
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')
            username = request.POST.get("username").lower().strip()
            email = request.POST.get("email").lower().replace(' ', '')
            school_name  = request.POST.get("school_name")
            course_of_study  = request.POST.get("course_of_study")
            matric_number  = request.POST.get("matric_number")
            internship_duration  = request.POST.get("internship_duration")
            password = request.POST.get("password1")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            payment  = request.POST.get("payment")
            course_choice = request.POST.get("course")
            amount_paid = request.POST.get("amount_paid")
            date_of_payment = request.POST.get("date_of_payment")
            commencement_date = request.POST.get("commencement_date")
            next_first_name = request.POST.get("next_first_name")
            next_last_name = request.POST.get("next_last_name")
            next_email = request.POST.get("next_email")
            next_phone = request.POST.get("next_phone")
            relation = request.POST.get("relation")
            installmental_payment = request.POST.get("installmental_payment")
            payment_method = request.POST.get("payment_method")
            upfront_due_date = request.POST.get("due_date_30")
            portion_type = request.POST.get("portion_type")
            portion_values = request.POST.getlist("portion_value")
            print(portion_values)


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
                    # Always lookup by unique key only (trainee_name). Use defaults OR update if already exists.
                    trainees = user.trainee

                  # Prepare values to set/update
                    trainees.gender = gender
                    trainees.address = address
                    trainees.category = category
                    trainees.name_of_school = school_name
                    trainees.state = state
                    trainees.city = city
                    trainees.country = country
                    trainees.phone = phone
                    trainees.course_of_study = course_of_study
                    trainees.matric_number = matric_number
                    trainees.duration_of_intership = internship_duration
                    trainees.payment_option = payment
                    trainees.commencement_date = commencement_date
                    trainees.nok_first_name = next_first_name
                    trainees.nok_last_name = next_last_name
                    trainees.nok_email = next_email
                    trainees.nok_phone = next_phone
                    trainees.nok_relationship = relation
                    trainees.portion_type = portion_type
                    trainees.course_id = Courses.objects.get(id=course_choice)
                    trainees.save()

                    # Handle portion_type == "Level" safely:
                    if portion_type == "Level":
                        # Normalize selected ids
                        selected_ids = [int(x) for x in portion_values if x and str(x).isdigit()]
                        if not selected_ids:
                            messages.error(request, "No levels were selected.")
                            return redirect("add_trainee")

                        # Fetch levels that belong to the chosen course
                        levels_qs = Level.objects.filter(id__in=selected_ids, course_id=trainees.course_id)                        
                        if not levels_qs.exists():
                            messages.error(request, "Selected levels are invalid for the chosen course.")                          
                            return redirect("add_trainee")

                        total_levels = Level.objects.filter(course_id=trainees.course_id).count()
                        if total_levels and levels_qs.count() >= total_levels:
                            messages.error(request, "You cannot select all levels. Please select fewer levels or choose Full Course.")
                            return redirect("add_trainee")
                        # Ensure instance saved before setting M2M
                        trainees.save()
                        # Safe M2M assignment — require a ManyToMany 'levels' field on Trainee model
                        if hasattr(trainees, 'levels') and hasattr(trainees.levels, 'set'):
                            trainees.levels.set(levels_qs)
                            print(trainees.levels.all())
                            trainees.save()
                        else:
                            messages.error(request, "Trainee model does not have a 'levels' ManyToManyField; update model/migrations.")
                            return redirect("add_trainee")
                    else:
                        # Full course selected: clear any M2M if present
                        if hasattr(trainees, 'levels') and hasattr(trainees.levels, 'clear'):
                            trainees.levels.clear()
                        trainees.save()
                except Exception as ex:
                    print(ex)
                    messages.error(request, "An error saving the Trainee details occured")
                    return redirect("add_trainee")
                try: 
                
                    course_price = float(Courses.objects.get(id=course_choice).price or 0)
                    course_months = int(Courses.objects.get(id=course_choice).months or 1)
                    if portion_type == "Level" and portion_values:
                        total_levels = Level.objects.filter(course_id=Courses.objects.get(id=course_choice)).count()
                        selected_levels = len(portion_values)
                        per_level_price = course_price / total_levels if total_levels else 0
                        final_price = per_level_price * selected_levels
                        months = selected_levels
                    else:
                        final_price = course_price
                        months = course_months

                    payment_histories = []
                    try:
                        amt_paid_val = float(amount_paid) if amount_paid not in (None, "") else 0.0
                    except Exception:
                        amt_paid_val = 0.0
                    if payment == "Full Payment":
                        payment_histories.append(PaymentHistory(
                            trainee=trainees,
                            course=Courses.objects.get(id=course_choice),
                            amount_paid=float(amt_paid_val),
                            installmental_payment="1",
                            payment_date=date_of_payment,
                            upfront_due_date=None,
                            payment_method=payment_method,
                            payment_option = payment,
                        ))
                    elif payment == "70% upfront and 30% later":
                        # First installment

                        payment_histories.append(PaymentHistory(
                            trainee=trainees,
                            course=Courses.objects.get(id=course_choice),
                            amount_paid=amt_paid_val,
                            installmental_payment="1",
                            payment_date=date_of_payment,
                            upfront_due_date=upfront_due_date,
                            payment_method=payment_method,
                            payment_option = payment
                        ))
                        # Second installment (not paid yet, create as pending)
                        payment_histories.append(PaymentHistory(
                            trainee=trainees,
                            course=Courses.objects.get(id=course_choice),
                            amount_paid=0.0,
                            installmental_payment="2",
                            payment_date=None,
                            upfront_due_date=upfront_due_date,
                            payment_method=payment_method,
                        ))
                    elif payment == "Monthly Payment":
                        if months <= 1:
                            messages.error(request, "Monthly payment is not available for this course/selection.")
                            return redirect("add_trainee")
                        
                        # Create PaymentHistory for each installment (first paid, rest pending)
                        monthly_amount = round(final_price / months, 2)
                        paid_installment = int(installmental_payment or 1)
                        for i in range(1, months + 1):
                            paid = amount_paid if i == paid_installment else 0.0
                            payment_histories.append(PaymentHistory(
                                trainee=trainees,
                                course=Courses.objects.get(id=course_choice),
                                amount_paid=paid,
                                installmental_payment=str(i),
                                payment_date=date_of_payment if i == paid_installment else None,
                                upfront_due_date=None,
                                payment_method=payment_method,
                                payment_option = payment
                            ))
                    
                    for ph in payment_histories:
                        ph.save()
                    # Optionally, set the latest payment as the current paymenthistory_id
                    if payment_histories:
                        trainees.paymenthistory_id = payment_histories[0]
                    trainees.save()
                    user.save()

                    # send_add_trainee(first_name, middle_name, last_name, username, password, schoolname, SCHOOL_NUM1, SCHOOL_NUM2, SCHOOL_WEB, ALOWED_HOST_ONLINE, email)
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

@login_required(login_url="/")
def get_levels_for_course(request):
    course_id = request.GET.get('course_id')
    levels = []
    if course_id:
        levels_qs = Level.objects.filter(course_id=course_id)
        levels = [{"id": lvl.id, "level": lvl.level} for lvl in levels_qs]
    return JsonResponse({"levels": levels})

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
            month = request.POST.get("month")
            presentations = request.POST.get("presentations")

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
                    new_course = Courses.objects.create(course_name=course_name , price=price_value, months=month, number_of_presentation=presentations)
                    

                    i = 1
                    while True:
                        level_name = request.POST.get(f'level_name_{i}')
                        level_desc = request.POST.get(f'level_desc_{i}')
                        if not level_name:
                            break
                        Level.objects.create(
                            level=level_name,
                            course_id=new_course,
                            descriptions=level_desc if level_desc else ""
                            # You can add a description field to Level if needed
                        )
                        i += 1

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

# @login_required(login_url="/")
# def view_course(request):
#     courses_list = Courses.objects.prefetch_related(
#         'level_set',
#         'trainercourseassignment_set__trainer_id__trainer_name'
#     ).annotate(num_trainees=Count('trainees')).order_by('id')

#     page_number = request.GET.get('page')
#     paginator = Paginator(courses_list, 10)
#     page_obj = paginator.get_page(page_number)

#     context = {
#         'total_course': paginator.count,
#         'courses': page_obj,
#         'page_obj': page_obj,
#     }
#     return render(request, 'admin_template/display_course.html', context)

@login_required(login_url="/")
def view_course(request):
    courses = Courses.objects.prefetch_related(
        'level_set',
        'trainercourseassignment_set__trainer_id__trainer_name'
    )

    context = {
        'total_course': courses,
    }
    return render(request, 'admin_template/display_course.html', context)

@login_required(login_url="/")
def course_details(request, course_id):
    course = Courses.objects.prefetch_related(
        'level_set',
        'trainercourseassignment_set__trainer_id__trainer_name'
    ).filter(id=course_id).first()
    
    if not course:
        messages.error(request, "Course not found.")
        return redirect('view_course')
    
    # Get course assignments (trainers assigned to this course)
    course_assignments = TrainerCourseAssignment.objects.filter(
        course_id=course
    ).select_related('trainer_id__trainer_name', 'level_id')
    
    # Count active trainees for this course
    active_trainees_count = Trainee.objects.filter(
        course_id=course,
        completed=False,
        suspended=False,
        terminated=False
    ).count()

    context = {
        'course_details': course,
        'course_assignments': course_assignments,
        'active_trainees_count': active_trainees_count,
    }
    return render(request, 'admin_template/course_details_professional.html', context)


@login_required(login_url="/")
def assign_trainer(request):
    courses = Courses.objects.prefetch_related('level_set').all()
    trainers = Trainers.objects.all()

    assigned_courses = []
    assigned_levels = {}
    selected_trainer = None

    if request.method == "POST":
        trainer_id = request.POST.get('trainer_id')
        trainer = get_object_or_404(Trainers, id=trainer_id)
        selected_trainer = trainer

        # Get already assigned courses/levels for this trainer
        assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer)
        assigned_courses = assignments.values_list('course_id', flat=True).distinct()
        assigned_levels = {}
        for assignment in assignments:
            assigned_levels.setdefault(assignment.course_id.id, []).append(assignment.level_id.id)

        # Get selected course IDs (from multi-select)
        course_ids = request.POST.getlist('course_ids')
        assignment_summary = []
        for course_id in course_ids:
            course = get_object_or_404(Courses, id=course_id)
            level_ids = request.POST.getlist(f'level_ids_{course_id}')
            level_names = []
            for level_id in level_ids:
                level = get_object_or_404(Level, id=level_id)
                # Prevent duplicate assignment
                if not TrainerCourseAssignment.objects.filter(trainer_id=trainer, course_id=course, level_id=level).exists():
                    TrainerCourseAssignment.objects.create(
                        trainer_id=trainer,
                        course_id=course,
                        level_id=level
                    )
                level_names.append(level.level)
            if level_names:
                assignment_summary.append({
                    "course_name": course.course_name,
                    "levels": level_names
                })

        # Send assignment notification email once, after all assignments
        if assignment_summary:
            try:
                sent = send_assign_trainer(
                    trainer=trainer,
                    schoolname=schoolname,
                    assignments=assignment_summary,
                    ALOWED_HOST_ONLINE=ALOWED_HOST_ONLINE,
                    email=trainer.trainer_name.email
                )
                if not sent:
                    messages.error(request, "Email not sent check your internet connection")
            except Exception as email_ex:
                print(f"Error sending assignment email: {email_ex}")
        messages.success(request, "Trainer assignments saved successfully.")
        return redirect('assign_trainer')

    # If GET and trainer selected, show assigned courses/levels
    elif request.method == "GET" and request.GET.get('trainer_id'):
        trainer_id = request.GET.get('trainer_id')
        trainer = get_object_or_404(Trainers, id=trainer_id)
        selected_trainer = trainer
        assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer)
        assigned_courses = assignments.values_list('course_id', flat=True).distinct()
        assigned_levels = {}
        for assignment in assignments:
            assigned_levels.setdefault(assignment.course_id.id, []).append(assignment.level_id.id)

    context = {
        "courses": courses,
        "trainers": trainers,
        "assigned_courses": assigned_courses,
        "assigned_levels": assigned_levels,
        "selected_trainer": selected_trainer,
    }
    return render(request, "admin_template/assign_trainer.html", context)

@login_required(login_url="/")
def assign_trainee(request):
    trainees = Trainee.objects.all()
    context = {
        "trainees": trainees,
    }

    if request.method == "POST":
        trainee_id = request.POST.get('trainee')
        course_id = request.POST.get('course')
        
        # Parse the {level_id: trainer_id} assignments from the form
        assignments = {}
        for key in request.POST:
            if key.startswith('trainer_for_level_'):
                level_id = key.replace('trainer_for_level_', '')
                trainer_id = request.POST.get(key)
                
                # Ensure trainer_id is not empty, otherwise skip
                if trainer_id:
                    assignments[level_id] = trainer_id

        # Validate that all required fields are present
        if not trainee_id or not course_id or not assignments:
            messages.error(request, "Please select a trainee, course, and assign trainers for all selected levels.")
            return redirect('assign_trainee')

        try:
            # Fetch the main objects *before* the transaction
            trainee = get_object_or_404(Trainee, id=trainee_id)
            course = get_object_or_404(Courses, id=course_id)
            
            # --- Professional Implementation: Use a Database Transaction ---
            # transaction.atomic() ensures that all database operations
            # either succeed together or fail together. If an error
            # occurs, all changes (including the delete) are rolled back.
            with transaction.atomic():
                
                # 1. Delete all previous assignments for this trainee and this course
                # This is the "replace" logic you requested.
                TraineeCourseAssignment.objects.filter(
                    trainee_id=trainee, 
                    course_id=course
                ).delete()

                assigned_count = 0
                
                # 2. Create the new assignments from the form data
                for level_id, trainer_id in assignments.items():
                    level = get_object_or_404(Level, id=level_id)
                    trainer = get_object_or_404(Trainers, id=trainer_id)
                    
                    # We can now create directly, as all old records are gone.
                    TraineeCourseAssignment.objects.create(
                        trainee_id=trainee,
                        trainer_id=trainer,
                        course_id=course,
                        level_id=level
                    )
                    assigned_count += 1

            if assigned_count > 0:
                messages.success(request, f"Successfully updated assignments for {trainee.trainee_name.first_name} in {course.course_name}.")
            else:
                # This would only happen if the form submission was empty
                messages.warning(request, "No assignments were created. Please check the form.")

        except Exception as e:
            # Catch any database or object-not-found errors
            print(f"Error during assignment: {e}") # Log the error for debugging
            messages.error(request, f"An error occurred while updating assignments. Error: {e}")
            
        return redirect('assign_trainee')

    return render(request, "admin_template/assign_trainee.html", context)

# AJAX: Get trainers for selected levels in a course
@login_required(login_url="/")
def get_trainers_for_levels(request, course_id):
    level_ids = request.GET.getlist('level_ids[]')
    result = {}
    for level_id in level_ids:
        assignments = TrainerCourseAssignment.objects.filter(course_id__id=course_id, level_id__id=level_id)
        trainers = [
            {
                "id": a.trainer_id.id,
                "name": f"{a.trainer_id.trainer_name.first_name} {a.trainer_id.trainer_name.last_name}"
            }
            for a in assignments
        ]
        result[level_id] = trainers
    return JsonResponse({"trainers_by_level": result})

# AJAX: Get course for a trainee
@login_required(login_url="/")
def get_trainee_course(request, trainee_id):
    trainee = get_object_or_404(Trainee, id=trainee_id)
    course = trainee.course_id
    if course:
        return JsonResponse({"id": course.id, "name": course.course_name})
    return JsonResponse({}, status=404)

# AJAX: Get trainers for a course
@login_required(login_url="/")
def get_course_trainers(request, course_id):
    assignments = TrainerCourseAssignment.objects.filter(course_id__id=course_id)
    data = [
        {
            "id": a.trainer_id.id,
            "name": f"{a.trainer_id.trainer_name.first_name} {a.trainer_id.trainer_name.last_name}"
        }
        for a in assignments
    ]
    return JsonResponse({"trainers": data})

# AJAX: Get levels for a course
@login_required(login_url="/")
def get_course_levels(request, course_id):
    levels = Level.objects.filter(course_id__id=course_id)
    data = [
        {"id": l.id, "name": l.level}
        for l in levels
    ]
    return JsonResponse({"levels": data})

# AJAX endpoint to fetch assigned courses/levels for a trainer
@login_required(login_url="/")
def get_trainer_assignments(request, trainer_id):
    trainer = get_object_or_404(Trainers, id=trainer_id)
    assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer)
    data = {}
    for assignment in assignments:
        course_id = assignment.course_id.id
        level_id = assignment.level_id.id
        data.setdefault(str(course_id), []).append(level_id)
    return JsonResponse(data)

@require_POST
def remove_trainer_assignment(request):
    trainer_id = request.POST.get('trainer_id')
    course_id = request.POST.get('course_id')
    level_id = request.POST.get('level_id')
    try:
        assignment = TrainerCourseAssignment.objects.get(
            trainer_id_id=trainer_id,
            course_id_id=course_id,
            level_id_id=level_id
        )
        assignment.delete()
        return JsonResponse({'success': True})
    except TrainerCourseAssignment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Assignment not found.'}, status=404)

@login_required(login_url="/")
def get_current_trainer(request, course_id):
    course = get_object_or_404(Courses, id=course_id)
    if course.trainer_id:
        trainer_name = f"{course.trainer_id.trainer_name.first_name} {course.trainer_id.trainer_name.last_name}"
    else:
        trainer_name = None
    return JsonResponse({'trainer': trainer_name})
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
@login_required(login_url="/")
def get_trainee_details(request, trainee_id):
    """
    Return trainee's course, course levels, trainee.level(s) and current assignments.
    JSON:
    { course: {id,name}, levels: [{id,name,description}], trainee_level_ids: [..], is_full_course: bool, assigned_trainers: { levelId: trainerId, course: trainerId } }
    """
    try:
        trainee = Trainee.objects.select_related('course_id', 'trainee_name').get(pk=trainee_id)
    except Trainee.DoesNotExist:
        return JsonResponse({'error': 'no trainee'}, status=404)

    course = trainee.course_id
    course_data = {'id': course.id, 'name': getattr(course, 'course_name', str(course))} if course else None

    # get all levels for course — use actual model field names, then map to 'name'/'description' keys for the frontend
    levels_qs = Level.objects.filter(course_id=course).values('id', 'level', 'descriptions')
    levels = []
    for l in levels_qs:
        levels.append({
            'id': l['id'],
            'name': l.get('level') or '',
            'description': l.get('descriptions') or ''
        })

    # trainee levels: handle both M2M 'levels' or single FK 'level'
    trainee_level_ids = []
    if hasattr(trainee, 'levels'):
        trainee_level_ids = [str(l.id) for l in trainee.levels.all()]
    elif hasattr(trainee, 'level') and getattr(trainee, 'level'):
        trainee_level_ids = [str(getattr(trainee, 'level').id)]

    # determine if trainee is full course (portion_type or lack of levels)
    is_full_course = (getattr(trainee, 'portion_type', '') != 'Level') or (len(trainee_level_ids) == 0)

    # fetch existing TraineeCourseAssignment entries for this trainee+course to pre-select trainers
    assigned = {}
    try:
        tca_qs = TraineeCourseAssignment.objects.filter(trainee_id=trainee, course_id=course)
        for a in tca_qs:
            level_obj = getattr(a, 'level_id', None)
            trainer_obj = getattr(a, 'trainer_id', None)
            if level_obj:
                assigned[str(getattr(level_obj, 'id', level_obj))] = str(getattr(trainer_obj, 'id', trainer_obj))
            else:
                assigned['course'] = str(getattr(trainer_obj, 'id', trainer_obj))
    except Exception:
        assigned = {}

    return JsonResponse({
        'course': course_data,
        'levels': levels,
        'trainee_level_ids': trainee_level_ids,
        'is_full_course': is_full_course,
        'assigned_trainers': assigned
    })

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
            profile_pic = request.FILES.get('profile_pic')
            username = request.POST.get("username").lower().strip()
            email = request.POST.get("email").lower().replace(' ', '')
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            birthday = request.POST.get("birthday")
            commission = request.POST.get('commission_rate')
            
            # Get selected skill expertise and competent skills
            selected_skill_expertise = request.POST.getlist("skill_expertise")
            selected_competent_skills = request.POST.getlist("competent_skills")
            
            account_no = request.POST.get("account_no")
            bank = request.POST.get("bank")

            if email != user.email:
                if CustomUser.objects.filter(email__iexact=email).exists():
                    messages.error(request, "Email already exists!")
                    return redirect("edit_trainer",trainer)
                else:
                    user.email = email
            
            elif gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
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
            trainers.state = state
            trainers.city = city
            trainers.country = country
            trainers.phone = phone
            trainers.account_no = account_no
            trainers.birthday = birthday
            trainers.bank = bank
            trainers.commission_rate = commission
            trainers.save()
            
            # Update many-to-many relationships
            if selected_skill_expertise:
                skill_expertise_objects = SkillExpertise.objects.filter(id__in=selected_skill_expertise)
                trainers.skill_expertise.set(skill_expertise_objects)
            else:
                trainers.skill_expertise.clear()
            
            if selected_competent_skills:
                competent_skills_objects = CompetentSkill.objects.filter(id__in=selected_competent_skills)
                trainers.competent_skills.set(competent_skills_objects)
            else:
                trainers.competent_skills.clear()

            messages.success(request, "Trainer Edited Successfully")
            return redirect("edit_trainer",trainer)

        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexcepted error occured")
            return redirect("edit_trainer",trainer)
    
    skill_expertise = SkillExpertise.objects.prefetch_related('competent_skills').all()
    content = {
        "trainer": trainers,
        "skill_expertise": skill_expertise,
    }
    return render(request, "admin_template/edit_trainer.html", content)

@login_required(login_url="/")
def edit_trainee(request, trainee):
    user = get_object_or_404(CustomUser, username=trainee)
    trainees = get_object_or_404(Trainee, trainee_name=user)
    courses = Courses.objects.all()
    payment_history_qs = PaymentHistory.objects.filter(trainee=trainees).first()
    levels_qs = None
    frontend_payment_show = trainees.commencement_date
    if request.method == "POST":
        try:
            # --- gather form data ---
            first_name = request.POST.get("first_name", "").capitalize()
            middle_name = request.POST.get("middle_name", "").capitalize()
            last_name = request.POST.get("last_name", "").capitalize()
            category = request.POST.get("category")
            gender = request.POST.get("gender")
            phone  = request.POST.get("phone")
            profile_pic = request.FILES.get('profile_pic')
            username = request.POST.get("username", "").lower().strip()
            email = request.POST.get("email", "").lower().replace(' ', '')
            school_name  = request.POST.get("school_name")
            course_of_study  = request.POST.get("course_of_study")
            matric_number  = request.POST.get("matric_number")
            internship_duration  = request.POST.get("internship_duration")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            country = request.POST.get("country")
            payment  = request.POST.get("payment")
            course_choice = request.POST.get("course")
            amount_paid = request.POST.get("amount_paid")
            date_of_payment = request.POST.get("date_of_payment")
            commencement_date = request.POST.get("commencement_date")
            next_first_name = request.POST.get("next_first_name")
            next_last_name = request.POST.get("next_last_name")
            next_email = request.POST.get("next_email")
            next_phone = request.POST.get("next_phone")
            relation = request.POST.get("relation")
            installmental_payment = request.POST.get("installmental_payment")
            payment_method = request.POST.get("payment_method")
            upfront_due_date = request.POST.get("upfront_due_date") or request.POST.get("due_date_30")
            portion_type = request.POST.get("portion_type")
            portion_values = request.POST.getlist("portion_value")  # list of ids as strings

            # --- validations (same style as add_trainee_save) ---
            if email and email != user.email and CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, "Email already exists!")
                return redirect("edit_trainee", trainee)

            if gender == "Select Gender":
                messages.error(request, "Select Student Gender!")
                return redirect("edit_trainee", trainee)

            if phone and (len(phone) < 11 or len(phone) > 15):
                messages.error(request, "Input an appropriate phone number")
                return redirect("edit_trainee", trainee)

            if username and username != user.username and CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return redirect("edit_trainee", trainee)

            # --- update user ---
            user.first_name = first_name
            user.middle_name = middle_name
            user.last_name = last_name
            if email:
                user.email = email
            if username:
                user.username = username
            if profile_pic:
                user.profile_pic = profile_pic
            user.save()

            # --- update trainee fields ---
            trainees.gender = gender
            trainees.address = address
            trainees.category = category
            trainees.name_of_school = school_name
            trainees.state = state
            trainees.city = city
            trainees.country = country
            trainees.phone = phone
            trainees.course_of_study = course_of_study
            trainees.matric_number = matric_number
            trainees.duration_of_intership = internship_duration
            trainees.payment_option = payment
            trainees.commencement_date = commencement_date
            trainees.nok_first_name = next_first_name
            trainees.nok_last_name = next_last_name
            trainees.nok_email = next_email
            trainees.nok_phone = next_phone
            trainees.nok_relationship = relation
            trainees.portion_type = portion_type

            # course assignment
            if course_choice:
                selected_course = Courses.objects.get(id=course_choice)
                trainees.course_id = selected_course
            trainees.save()

            # --- handle Level selection (M2M safe) ---
            if portion_type == "Level":
                # normalize incoming ids
                selected_ids = [int(x) for x in portion_values if x and str(x).isdigit()]
                if not selected_ids:
                    messages.error(request, "No levels were selected.")
                    return redirect("edit_trainee", trainee)

                # fetch only levels that belong to the selected course
                levels_qs = Level.objects.filter(id__in=selected_ids, course_id=trainees.course_id)
                if not levels_qs.exists():
                    messages.error(request, "Selected levels are invalid for the chosen course.")
                    return redirect("edit_trainee", trainee)

                total_levels = Level.objects.filter(course_id=trainees.course_id).count()
                if total_levels and levels_qs.count() >= total_levels:
                    messages.error(request, "You cannot select all levels. Please select fewer levels or choose Full Course.")
                    return redirect("edit_trainee", trainee)

                # ensure trainee persisted
                trainees.save()
                try:
                    trainees.refresh_from_db()
                except Exception:
                    pass

                # Replace M2M safely (this removes previous links and sets only the selected ones)
                if hasattr(trainees, 'levels') and hasattr(trainees.levels, 'set'):
                    # with transaction.atomic():
                    # clear existing links then set new ones (atomic)
                    print("Check b4 clear", trainees.levels.all())
                    trainees.levels.clear()
                    print("Lemme check here for clear", trainees.levels.all())
                    trainees.levels.set(levels_qs)
                    print("For seting new one", trainees.levels.all())
                    trainees.save()
                    print("After setting ", trainees.levels.all())

                    # delete any TraineeCourseAssignment entries for this trainee+course
                    # that refer to levels NOT in the new selection (remove stale assignments)
                    TraineeCourseAssignment.objects.filter(
                        trainee_id=trainees,
                        course_id=trainees.course_id
                    ).exclude(level_id__in=levels_qs).delete()
                    print("After setting 2", trainees.levels.all())
                else:
                    # fallback for older FK schema: set first matched level
                    if hasattr(trainees, 'level'):
                        trainees.levels = levels_qs.first()
                        print("Are you here?")
                        trainees.save()
                        # remove per-level assignments for other levels for same course
                        TraineeCourseAssignment.objects.filter(
                            trainee_id=trainees,
                            course_id=trainees.course_id
                        ).exclude(level_id=trainees.levels).delete()
                    else:
                        messages.error(request, "Trainee model does not have a 'levels' ManyToManyField; update model/migrations.")
                        return redirect("edit_trainee", trainee)
            else:
                # Full course selected: clear any M2M and remove per-level assignments for the course
                if hasattr(trainees, 'levels') and hasattr(trainees.levels, 'clear'):
                    trainees.levels.clear()
                    print("Checking again for clearity", trainees.levels.all())
                trainees.save()
                # delete per-level assignments for this trainee + course
                TraineeCourseAssignment.objects.filter(trainee_id=trainees, course_id=trainees.course_id).delete()

            # --- update PaymentHistory for this course: remove old entries for this course and recreate ---
            try:
                if selected_course:
                    # ensure trainee persisted
                    trainees.save()
                    # defensive check: trainee must exist in DB
                    if not Trainee.objects.filter(pk=getattr(trainees, 'pk', None)).exists():
                        messages.error(request, "Trainee record not found. Cannot update payment history.")
                        return redirect("edit_trainee", trainee)

                    # re-fetch a fresh DB-backed Trainee instance and use it for FK inserts
                    trainee_db = Trainee.objects.get(pk=trainees.pk)

                    # parse numeric safely
                    try:
                        amt_paid_val = float(amount_paid) if amount_paid not in (None, "") else 0.0
                    except Exception:
                        amt_paid_val = 0.0

                    # compute final_price and months depending on selection
                    course_price = float(selected_course.price or 0)
                    course_months = int(selected_course.months or 1)
                    if portion_type == "Level" and portion_values:
                        total_levels = Level.objects.filter(course_id=selected_course).count()
                        selected_levels = len([x for x in portion_values if x and str(x).isdigit()])
                        per_level_price = course_price / total_levels if total_levels else 0
                        final_price = per_level_price * selected_levels
                        months = selected_levels or 1
                    else:
                        final_price = course_price
                        months = course_months

                    # Detect payment option change: check existing histories for this trainee+course
                    existing_ph_qs = PaymentHistory.objects.filter(trainee=trainee_db, course=selected_course)
                    previous_payment_option = existing_ph_qs.order_by("id").first()
                    old_payment_type = previous_payment_option.payment_option if previous_payment_option else None

                    # if payment option changed -> recreate; otherwise update first entry
                    recreate = (old_payment_type != payment)

                    if recreate:
                        with transaction.atomic():
                            # remove old entries first
                            trainee_db.paymenthistory_id = None
                            trainee_db.save()
                            try:
                                existing_ph_qs.delete()
                                print(trainees.commencement_date)
                            except Exception as e:
                                print(f"It has an error deleting {e}")
                                messages.error(request, "It has an error deleting")
                                return redirect("edit_trainee", trainee) 

                            new_ph = []
                            if payment == "Full Payment":
                                new_ph.append(PaymentHistory(
                                    trainee=trainees,
                                    course=selected_course,
                                    amount_paid=amt_paid_val,
                                    installmental_payment="1",
                                    payment_date=date_of_payment or None,
                                    upfront_due_date=None,
                                    payment_method=payment_method,
                                    payment_option=payment,
                                ))
                            elif payment == "70% upfront and 30% later":
                                upfront_amt = round(final_price * 0.7, 2)
                                new_ph.append(PaymentHistory(
                                    trainee=trainees,
                                    course=selected_course,
                                    amount_paid=amt_paid_val,
                                    installmental_payment="1",
                                    payment_date=date_of_payment or None,
                                    upfront_due_date=upfront_due_date or None,
                                    payment_method=payment_method,
                                    payment_option=payment,
                                ))
                                new_ph.append(PaymentHistory(
                                    trainee=trainees,
                                    course=selected_course,
                                    amount_paid=0.0,
                                    installmental_payment="2",
                                    payment_date=None,
                                    upfront_due_date=upfront_due_date or None,
                                    payment_method=payment_method,
                                    payment_option=payment,
                                ))
                            elif payment == "Monthly Payment":
                                if months <= 1:
                                    messages.error(request, "Monthly payment is not available for this course/selection.")
                                    return redirect("edit_trainee", trainee)
                                paid_installment = int(installmental_payment or 1)
                                for i in range(1, months + 1):
                                    paid = amt_paid_val if i == paid_installment else 0
                                    new_ph.append(PaymentHistory(
                                        trainee=trainees,
                                        course=selected_course,
                                        amount_paid=paid,
                                        installmental_payment=str(i),
                                        payment_date=(date_of_payment if i == paid_installment else None),
                                        upfront_due_date=None,
                                        payment_method=payment_method,
                                        payment_option=payment,
                                    ))

                            # Save new payment history entries using the DB-backed trainee instance
                            for ph in new_ph:
                                ph.save()

                            if new_ph:
                                trainees.paymenthistory_id = new_ph[0]
                                # Only set trainee levels if we actually have a queryset/iterable of levels.
                                if levels_qs is not None and hasattr(trainees, 'levels') and hasattr(trainees.levels, 'set'):
                                    trainees.levels.set(levels_qs)
                                    trainees.save()
                                trainee_db.save()
                    else:
                        # same payment option: update the primary history row (non-destructive)
                        primary_ph = existing_ph_qs.order_by('id').first()
                        if primary_ph:
                            primary_ph.amount_paid = amt_paid_val
                            primary_ph.payment_method = payment_method or primary_ph.payment_method
                            primary_ph.payment_date = date_of_payment or primary_ph.payment_date
                            primary_ph.upfront_due_date = upfront_due_date or primary_ph.upfront_due_date
                            primary_ph.save()
                            trainees.paymenthistory_id = primary_ph
                            trainee_db.save()
                            trainees.save()

                    messages.success(request, "Trainee Edited Successfully")
            except Exception as ph_ex:
                print("PaymentHistory error:", ph_ex)
                messages.error(request, "Payment history update failed.")
                return redirect("edit_trainee", trainee)

            
        except Exception as excepts:
            print(excepts)
            messages.error(request, "An Unexpected error occurred")
            return redirect("edit_trainee", trainee)
            
    # GET: render form with existing data
    content = {
        "trainee": trainees,
        "courses": courses,
        "commencement_date":frontend_payment_show,
        "due_date":payment_history_qs.upfront_due_date,
        "date_of_payment":payment_history_qs.payment_date,
    }
    return render(request, "admin_template/edit_trainee.html", content)

@login_required(login_url="/")
def edit_course(request, course):

    courses = get_object_or_404(Courses, id=course)
    levels = Level.objects.filter(course_id=courses)

    if request.method == "POST":
        course_name = request.POST.get("course")
        price = request.POST.get("price").strip()
        month = request.POST.get("month")
        presentations = request.POST.get("presentations")

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
        courses.months = month
        courses.number_of_presentation=presentations
        courses.save()

        # Update levels
        # Remove all existing levels for this course
        Level.objects.filter(course_id=courses).delete()
        i = 1
        while True:
            level_name = request.POST.get(f'level_name_{i}')
            level_desc = request.POST.get(f'level_desc_{i}')
            if not level_name:
                break
            Level.objects.create(
                level=level_name,
                course_id=courses,
                descriptions=level_desc if level_desc else ""
            )
            i += 1

        messages.success(request, f"The course '{courses.course_name}' has been successfully updated to '{course_name}' with the price NGN{price}'")
        return redirect("view_course")

    context = {
        'courses': courses,
        'levels': levels,
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
                    # Q(religion__icontains=search)|
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
                    # Q(religion__icontains=search)|
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
    courses = Courses.objects.all()
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        file = request.FILES.get("file")
        course_obj = None
        if category not in ["General", "Trainers", "Trainees"]:
            try:
                course_obj = Courses.objects.get(id=category)
                category_val = "Course"
            except Courses.DoesNotExist:
                course_obj = None
                category_val = "General"
        else:
            category_val = category
        try:
            announcement = Announcement.objects.create(
                title=title,
                description=description,
                file=file,
                category=category_val,
                course=course_obj
            )
            # Only mark as unread for intended recipients (do NOT add unintended users)
            # Do NOT add users to read_by here; leave read_by empty so only intended users see it as unread
            pass

            messages.success(request, "Announcement sent successfully")
        except Exception as e:
            print(e)
            messages.error(request, f"Announcement not sent due to {e}")

    context = {
        "courses": courses,
    }
    return render(request, "admin_template/send_announcement.html", context)

def get_user_announcements(user):
    # user_type is stored as string of int, but model uses int for comparison
    if str(user.user_type) == "1":  # Admin
        return Announcement.objects.all()
    elif str(user.user_type) == "2":  # Trainer
        try:
            trainer = Trainers.objects.get(trainer_name=user)
            trainer_courses = trainer.course_id.all()
            return Announcement.objects.filter(
                Q(category="General") |
                Q(category="Trainers") |
                (Q(category="Course") & Q(course__in=trainer_courses))
            )
        except Trainers.DoesNotExist:
            return Announcement.objects.none()
    elif str(user.user_type) == "3":  # Trainee
        try:
            trainee = Trainee.objects.get(trainee_name=user)
            return Announcement.objects.filter(
                Q(category="General") |
                Q(category="Trainees") |
                (Q(category="Course") & Q(course=trainee.course_id))
            )
        except Trainee.DoesNotExist:
            return Announcement.objects.none()
    return Announcement.objects.none()

@login_required(login_url="/")
def view_announcement(request):
    announcements = Announcement.objects.all()

    return render(request, "admin_template/view_announcement.html",{
        "announcements":announcements,
    })

def edit_announcement(request, announcement_title):
    courses = Courses.objects.all()
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
    return render(request, "admin_template/edit_announcement.html", {"announcement":announcement, "course":courses})

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
    trainee = Trainee.objects.filter(trainee_name=user).first()
    payment_history = PaymentHistory.objects.filter(trainee=trainee)
    monthly = None

    # Calculate total amount paid by summing all payment records for this trainee
    total_amount_paid = 0
    for payment in payment_history:
        if payment.amount_paid:
            try:
                total_amount_paid += float(payment.amount_paid)
            except (ValueError, TypeError):
                # Skip invalid payment amounts
                continue

    # Calculate remaining amount based on course price and total paid
    course_price = float(trainee.course_id.price) if trainee.course_id and trainee.course_id.price else 0
    
    if trainee.payment_option == "Monthly Payment":
        monthly = course_price // int(trainee.course_id.months) if trainee.course_id.months else 0
    
    remaining = course_price - total_amount_paid

    context={
        'user':user,
        'trainee':trainee,
        'payment_history': payment_history,
        'total_amount_paid': total_amount_paid,
        "remaining":remaining,
        "monthly":monthly,
    }

    return render(request, 'admin_template/view_trainee_details.html', context)

def trainer_details(request, username):
    user = get_object_or_404(CustomUser, username=username)
    trainer = get_object_or_404(Trainers, trainer_name=user)
    course = Courses.objects.filter(trainer_id=trainer)
    assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer)
    month = None

    total_salary = 0
    for assignment in assignments:
        trainees = TraineeCourseAssignment.objects.filter(
            trainer_id=trainer,
            course_id=assignment.course_id,
            level_id=assignment.level_id,
        )
        course_fee = assignment.course_id.price
        # Optionally filter trainees by payment date/month
        if month:
            trainees = trainees.filter(trainee_id__payments__date__month=month)
        total_salary += len(trainees) * int(course_fee)  # 30% example
    # return total_salary

    context={
        'user':user,
        'trainer':trainer,
        'course':course,
        'assignment':assignment,
        'total_salary':total_salary,
    }

    return render(request, 'admin_template/view_trainer_details.html', context)

def invite_admin(request):
    if request.method == "POST":
        email_used = request.POST.get("email")

        if email_used:
            token = create_access_token(data={"email": email_used})
            sent = send_invite_link(email=email_used, schoolname=schoolname, token=token)
            if not sent:
                messages.error(request, "Email not sent check your internet connection")
            messages.success(request, "Admin Invitated Successfully")
        else:
            messages.error(request, "Insert an email before submiting")

    return render(request, "admin_template/invite-admin.html")

def create_invited_admin(request, token):
    payload = decode_access_token(token)
    email = payload.get("email")

    if email:
        if request.method == "POST":
            username = request.POST.get("username").lower().strip()
            email = request.POST.get("email").lower().replace(' ', '')
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            profile_pic = request.FILES.get('profile_pic', 'blank.webp')

            if CustomUser.objects.filter(email__iexact=email).exists():
                messages.error(request, "Email already exists!")
                return render(request, "create-admin.html", {"request" : request.POST})
            
            elif CustomUser.objects.filter(username__iexact=username).exists():
                messages.error(request, "Username already exists!")
                return render(request, "create-admin.html", {"request" : request.POST})

            if password1 == password2:
                admin = CustomUser.objects.create(
                    username = username,
                    email = email,
                    password = password2,
                    profile_pics = profile_pic,
                    user_type = 4,
                )
                admin.save()
                messages.success(request, "Admin created successfully")
                return render(request, "index.html")
            else:
                messages.error(request, "Passwords does not match")
                return render(request, "create-admin.html", {"request" : request.POST})
    else:
        raise

    return render(request, "create-admin.html")

# def payment(request):
#     return render(request, "admin_template/payment.html")


@login_required(login_url="/")
def manage_skills(request):
    skill_expertise = SkillExpertise.objects.prefetch_related('competent_skills').all()
    courses = Courses.objects.all()
    context = {
        'skill_expertise': skill_expertise,
        "courses":courses,
    }
    return render(request, 'admin_template/manage_skills.html', context)

@login_required(login_url="/")
def add_skill_expertise(request):
    if request.method == "POST":
        try:
            expertise_name = request.POST.get("expertise_name").strip()
            expertise_description = request.POST.get("expertise_description", "").strip()
            
            if not expertise_name:
                messages.error(request, "Expertise name is required!")
                return redirect("manage_skills")
            
            if SkillExpertise.objects.filter(name__iexact=expertise_name).exists():
                messages.error(request, f"Skill expertise '{expertise_name}' already exists!")
                return redirect("manage_skills")
            
            SkillExpertise.objects.create(
                name=expertise_name,
                description=expertise_description
            )
            
            messages.success(request, f"Skill expertise '{expertise_name}' added successfully!")
            return redirect("manage_skills")
            
        except Exception as e:
            print(f"Error adding skill expertise: {e}")
            messages.error(request, "An error occurred while adding the skill expertise.")
            return redirect("manage_skills")
    
    return redirect("manage_skills")

@login_required(login_url="/")
def add_competent_skill(request):
    if request.method == "POST":
        try:
            skill_expertise_id = request.POST.get("skill_expertise_id")
            skill_name = request.POST.get("skill_name").strip()
            skill_description = request.POST.get("skill_description", "").strip()
            
            if not skill_expertise_id or not skill_name:
                messages.error(request, "Both expertise area and skill name are required!")
                return redirect("manage_skills")
            
            try:
                skill_expertise = SkillExpertise.objects.get(id=skill_expertise_id)
            except SkillExpertise.DoesNotExist:
                messages.error(request, "Selected expertise area does not exist!")
                return redirect("manage_skills")
            
            if CompetentSkill.objects.filter(name__iexact=skill_name, skill_expertise=skill_expertise).exists():
                messages.error(request, f"Skill '{skill_name}' already exists under '{skill_expertise.name}'!")
                return redirect("manage_skills")
            
            CompetentSkill.objects.create(
                name=skill_name,
                skill_expertise=skill_expertise,
                description=skill_description
            )
            
            messages.success(request, f"Skill '{skill_name}' added successfully under '{skill_expertise.name}'!")
            return redirect("manage_skills")
            
        except Exception as e:
            print(f"Error adding competent skill: {e}")
            messages.error(request, "An error occurred while adding the skill.")
            return redirect("manage_skills")
    
    return redirect("manage_skills")

@login_required(login_url="/")
@csrf_exempt
def delete_skill_expertise(request, expertise_id):
    if request.method == "POST":
        try:
            expertise = SkillExpertise.objects.get(id=expertise_id)
            expertise_name = expertise.name
            expertise.delete()
            messages.success(request, f"Skill expertise '{expertise_name}' deleted successfully!")
            return JsonResponse({'success': True})
        except SkillExpertise.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Expertise not found'})
        except Exception as e:
            print(f"Error deleting skill expertise: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url="/")
@csrf_exempt
def delete_competent_skill(request, skill_id):
    if request.method == "POST":
        try:
            skill = CompetentSkill.objects.get(id=skill_id)
            skill_name = skill.name
            skill.delete()
            messages.success(request, f"Skill '{skill_name}' deleted successfully!")
            return JsonResponse({'success': True})
        except CompetentSkill.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Skill not found'})
        except Exception as e:
            print(f"Error deleting competent skill: {e}")
            return JsonResponse({'success': False, 'error': 'An error occurred'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required(login_url="/")
def get_skills_by_expertise(request):
    """API endpoint to get competent skills for selected expertise areas"""
    expertise_ids = request.GET.getlist('expertise_ids[]')
    
    if not expertise_ids:
        return JsonResponse({'skills': []})
    
    try:
        skills = CompetentSkill.objects.filter(
            skill_expertise_id__in=expertise_ids
        ).select_related('skill_expertise').values(
            'id', 'name', 'description', 'skill_expertise__name', 'skill_expertise_id'
        )
        
        skills_data = list(skills)
        return JsonResponse({'skills': skills_data})
        
    except Exception as e:
        print(f"Error fetching skills: {e}")
        return JsonResponse({'skills': [], 'error': 'An error occurred'})
   
# def show_me_trainee(request):
#     return render(request, "admin_template/process_trainee_payment.html")