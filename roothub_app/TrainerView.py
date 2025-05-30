from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, AssignmentSubmission, Presentation, Trainers, Courses, Trainee, Fix_Class
from django.db.models import Q
from django.contrib import messages

@login_required(login_url="/")
def home(request):
    trainer = Trainers.objects.get(trainer_name=request.user)
    courses = Courses.objects.filter(trainer_id=trainer).all()
    dates = Presentation.objects.values_list('date', flat=True).distinct()
    trainer_courses = Courses.objects.filter(trainer_id=trainer)
    fix_classes = Fix_Class.objects.all()
    
    courses_with_trainees = []
    for course in courses:
        trainees_count = Trainee.objects.filter(course_id=course).count()
        courses_with_trainees.append({
            'course': course,
            'trainees_count': trainees_count
        })

    content = {
        'trainer': trainer,
        'courses_with_trainees': courses_with_trainees,
        "dates":dates,
        "trainer_courses":trainer_courses,
        "fix_classes":fix_classes
    }
    return render(request, "trainer_template/home.html", content)

@login_required(login_url="/")
def search(request):
    data=None
    try:
        if request.method == "POST":
            search = request.POST.get("search")
            if search:
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
                    "trainees":trainee_search,
                    "param":search
                }
    except Exception as e:
        print(e)
        messages.error(request, f"An error was encountered {e}")
    return render(request, "trainer_template/search.html", data)

@login_required(login_url="/")
def upload_assignment(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get("description")
        course_id = request.POST.get('course')
        due_date = request.POST.get('due_date')
        file = request.FILES.get('file')

        course = get_object_or_404(Courses, id=course_id)

        Assignment.objects.create(
            trainer=request.user,
            course=course,
            title=title,
            description=description,
            file=file,
            due_date=due_date
        )
        messages.success(request, "Assignment uploaded successfully")
        return redirect('upload_assignment')

    trainer = Trainers.objects.get(trainer_name=request.user)
    trainer_courses = Courses.objects.filter(trainer_id=trainer)
    return render(request, 'trainer_template/upload_assignment.html', {'trainer_courses': trainer_courses})

@login_required(login_url="/")
def view_submissions(request):
    try:
        # Get all assignments uploaded by the trainer
        assignments = Assignment.objects.filter(trainer=request.user)

        # Get all submissions for the trainer's assignments
        submissions = AssignmentSubmission.objects.filter(assignment__in=assignments)

        return render(request, 'trainer_template/view_submissions.html', {'submissions': submissions})

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("trainer_home")
    
@login_required(login_url="/")
def view_uploaded_assignments(request):
    try:
        # Get the trainer object
        # trainer = Trainers.objects.get(trainer_name=request.user)

        # Fetch assignments uploaded by the trainer
        assignments = Assignment.objects.filter(trainer=request.user)

        context = {
            'assignments': assignments,
        }
        return render(request, "trainer_template/view_upload_assignment.html", context)

    except Trainers.DoesNotExist:
        messages.error(request, "You are not registered as a trainer.")
        return redirect("trainer_home")
@login_required(login_url="/")
def edit_assignment(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    try:
        if request.method == 'POST':
            title = request.POST.get('title')
            description = request.POST.get("description")
            course_id = request.POST.get('course')
            due_date = request.POST.get('due_date')
            file = request.FILES.get('file')

            course = get_object_or_404(Courses, id=course_id)

            assignment.title = title
            assignment.description = description
            assignment.course = course
            assignment.due_date = due_date
            if file:
                assignment.file = file
            assignment.save()
            messages.success(request, "Assignment Updated suucessfully")
            return redirect("view_upload_assignment")
    except Exception as e:
        print(e)

    trainer = Trainers.objects.get(trainer_name=request.user)
    trainer_courses = Courses.objects.filter(trainer_id=trainer)
    return render(request, "trainer_template/edit_assignment.html",{"assignment":assignment,'trainer_courses': trainer_courses})

@login_required(login_url="/")
def delete_uploaded_assignment(request, assignment_title):
    # Get the assignment uploaded by the trainer
    assignments = get_object_or_404(Assignment, trainer=request.user, title=assignment_title)

    # Get any submissions related to the assignment
    submitted_assignments = AssignmentSubmission.objects.filter(assignment=assignments)

    # Delete the assignment and its submissions
    if submitted_assignments.exists():
        submitted_assignments.delete()
    assignments.delete()

    # Add a success message
    messages.success(request, f"The assignment title '{assignment_title}' and its submissions have been deleted successfully.")

    # Redirect to the page where the trainer can view uploaded assignments
    return redirect("view_upload_assignment")

@login_required(login_url="/")
def fix_classes(request):
    if request.method == 'POST':
        try:
            title = request.POST.get("title")
            description = request.POST.get("description")
            course_id = request.POST.get("course")
            class_date = request.POST.get("date_of_class")
            start_class = request.POST.get("start_class")
            end_class = request.POST.get("end_class")

            course = get_object_or_404(Courses, id=course_id)
            trainer = Trainers.objects.get(trainer_name=request.user)

            fix_class = Fix_Class.objects.create(
                title = title,
                description = description,
                course = course,
                trainer = trainer,
                class_date = class_date,
                start_class = start_class,
                end_class = end_class
            )    
            fix_class.save()
            messages.success(request, "Class has been fixed Successfully")
            return redirect("trainer_home")   
        except Exception as e:
            print(e)
            messages.error(request, f"{e}")
        return redirect("trainer_home")