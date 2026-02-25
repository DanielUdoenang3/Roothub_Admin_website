from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import (
    Assignment,
    AssignmentSubmission,
    Presentation,
    Trainers,
    Courses,
    Trainee,
    Fix_Class,
    TrainerCourseAssignment,
    TraineeCourseAssignment,
)
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse


@login_required(login_url="/")
def home(request):
    trainer = Trainers.objects.get(trainer_name=request.user)

    # Get all courses assigned to this trainer
    trainer_assignments = TrainerCourseAssignment.objects.filter(
        trainer_id=trainer
    ).select_related("course_id")

    # Get all trainees assigned to this trainer with course and level details
    trainee_assignments = TraineeCourseAssignment.objects.filter(
        trainer_id=trainer
    ).select_related("trainee_id", "course_id", "level_id")

    # Calculate statistics
    total_courses = trainer_assignments.count()
    total_trainees = trainee_assignments.count()

    # Get course names the trainer is offering
    course_names = [
        f"{assignment.course_id.course_name} - {assignment.level_id.level}"
        for assignment in trainer_assignments
    ]

    # Group trainees by course and level for detailed view
    trainee_details = []
    for assignment in trainee_assignments:
        trainee_info = {
            "trainee_name": (
                assignment.trainee_id.trainee_name.get_full_name()
                if assignment.trainee_id.trainee_name.first_name
                else assignment.trainee_id.trainee_name.username
            ),
            "course_name": assignment.course_id.course_name,
            "level": (
                assignment.level_id.level if assignment.level_id else "Full Course"
            ),
        }
        trainee_details.append(trainee_info)

    # Group trainees by course for summary
    from collections import defaultdict

    course_trainee_count = defaultdict(int)
    for assignment in trainee_assignments:
        course_trainee_count[assignment.course_id.course_name] += 1
    dates = Presentation.objects.values_list("date", flat=True).distinct()
    fix_classes = Fix_Class.objects.all()

    content = {
        "trainer": trainer,
        "dates": dates,
        "fix_classes": fix_classes,
        "total_courses": total_courses,
        "total_trainees": total_trainees,
        "course_names": course_names,
        "trainee_details": trainee_details,
        "trainer_assignments": trainer_assignments,
        "course_trainee_count": dict(course_trainee_count),
    }
    return render(request, "trainer_template/home.html", content)


@login_required(login_url="/")
def search(request):
    data = None
    try:
        if request.method == "POST":
            search = request.POST.get("search")
            if search:
                trainee_search = Trainee.objects.filter(
                    Q(trainee_name__username__icontains=search)
                    | Q(trainee_name__first_name__icontains=search)
                    | Q(trainee_name__middle_name__icontains=search)
                    | Q(trainee_name__last_name__icontains=search)
                    | Q(trainee_name__email__icontains=search)
                    | Q(phone__icontains=search)
                    | Q(state__icontains=search)
                    | Q(religion__icontains=search)
                    | Q(city__icontains=search)
                )
                data = {"trainees": trainee_search, "param": search}
    except Exception as e:
        print(e)
        messages.error(request, f"An error was encountered {e}")
    return render(request, "trainer_template/search.html", data)


@login_required(login_url="/")
def upload_assignment(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        course_id = request.POST.get("course")
        due_date = request.POST.get("due_date")
        file = request.FILES.get("file")

        course = get_object_or_404(Courses, id=course_id)

        Assignment.objects.create(
            trainer=request.user,
            course=course,
            title=title,
            description=description,
            file=file,
            due_date=due_date,
        )
        messages.success(request, "Assignment uploaded successfully")
        return redirect("upload_assignment")

    trainer = Trainers.objects.get(trainer_name=request.user)
    trainer_courses = Courses.objects.filter(trainer_id=trainer)
    return render(
        request,
        "trainer_template/upload_assignment.html",
        {"trainer_courses": trainer_courses},
    )


@login_required(login_url="/")
def view_submissions(request):
    try:
        # Get all assignments uploaded by the trainer
        assignments = Assignment.objects.filter(trainer=request.user)

        # Get all submissions for the trainer's assignments
        submissions = AssignmentSubmission.objects.filter(assignment__in=assignments)

        return render(
            request,
            "trainer_template/view_submissions.html",
            {"submissions": submissions},
        )

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
            "assignments": assignments,
        }
        return render(request, "trainer_template/view_upload_assignment.html", context)

    except Trainers.DoesNotExist:
        messages.error(request, "You are not registered as a trainer.")
        return redirect("trainer_home")


@login_required(login_url="/")
def edit_assignment(request, id):
    assignment = get_object_or_404(Assignment, id=id)
    try:
        if request.method == "POST":
            title = request.POST.get("title")
            description = request.POST.get("description")
            course_id = request.POST.get("course")
            due_date = request.POST.get("due_date")
            file = request.FILES.get("file")

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
    return render(
        request,
        "trainer_template/edit_assignment.html",
        {"assignment": assignment, "trainer_courses": trainer_courses},
    )


@login_required(login_url="/")
def delete_uploaded_assignment(request, assignment_title):
    # Get the assignment uploaded by the trainer
    assignments = get_object_or_404(
        Assignment, trainer=request.user, title=assignment_title
    )

    # Get any submissions related to the assignment
    submitted_assignments = AssignmentSubmission.objects.filter(assignment=assignments)

    # Delete the assignment and its submissions
    if submitted_assignments.exists():
        submitted_assignments.delete()
    assignments.delete()

    # Add a success message
    messages.success(
        request,
        f"The assignment title '{assignment_title}' and its submissions have been deleted successfully.",
    )

    # Redirect to the page where the trainer can view uploaded assignments
    return redirect("view_upload_assignment")


@login_required(login_url="/")
def fix_classes(request):
    if request.method == "POST":
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
                title=title,
                description=description,
                course=course,
                trainer=trainer,
                class_date=class_date,
                start_class=start_class,
                end_class=end_class,
            )
            fix_class.save()
            messages.success(request, "Class has been fixed Successfully")
            return redirect("trainer_home")
        except Exception as e:
            print(e)
            messages.error(request, f"{e}")
        return redirect("trainer_home")


@login_required(login_url="/")
def view_payment_calculation(request):
    """View payment calculation based on number of trainees"""
    trainer = get_object_or_404(Trainers, trainer_name=request.user)

    # Get all trainee assignments for this trainer
    trainee_assignments = TraineeCourseAssignment.objects.filter(
        trainer_id=trainer
    ).select_related("trainee_id", "course_id", "level_id")

    # Calculate payment details
    payment_breakdown = []
    total_earnings = 0

    # Group by course and level for calculation
    from collections import defaultdict

    course_level_groups = defaultdict(list)

    for assignment in trainee_assignments:
        key = (
            assignment.course_id.id,
            assignment.level_id.id if assignment.level_id else None,
        )
        course_level_groups[key].append(assignment)

    # Calculate earnings for each course-level combination
    for (course_id, level_id), assignments in course_level_groups.items():
        course = assignments[0].course_id
        level = assignments[0].level_id
        trainee_count = len(assignments)

        # Get course fee
        try:
            course_fee = float(course.price) if course.price else 0
        except (ValueError, TypeError):
            course_fee = 0

        # Get commission rate (default 30% if not set)
        try:
            commission_rate = (
                float(trainer.commission_rate) / 100
                if trainer.commission_rate
                else 0.30
            )
        except (ValueError, TypeError):
            commission_rate = 0.30

        # Calculate earnings for this course-level
        earnings_per_trainee = course_fee * commission_rate
        total_course_earnings = earnings_per_trainee * trainee_count
        total_earnings += total_course_earnings

        # Get trainee names for this course-level
        trainee_names = [
            assignment.trainee_id.trainee_name.get_full_name()
            for assignment in assignments
        ]

        payment_breakdown.append(
            {
                "course_name": course.course_name,
                "level_name": level.level if level else "Full Course",
                "trainee_count": trainee_count,
                "trainee_names": trainee_names,
                "course_fee": course_fee,
                "commission_rate": commission_rate * 100,
                "earnings_per_trainee": earnings_per_trainee,
                "total_course_earnings": total_course_earnings,
            }
        )

    # Get payment history
    from .models import TrainerPayroll

    payment_history = TrainerPayroll.objects.filter(trainer=trainer).order_by(
        "-created_at"
    )[:5]

    # Calculate total paid and pending
    total_paid = 0
    for payroll in TrainerPayroll.objects.filter(trainer=trainer):
        try:
            total_paid += float(payroll.amount_paid) if payroll.amount_paid else 0
        except (ValueError, TypeError):
            continue

    pending_amount = total_earnings - total_paid

    context = {
        "trainer": trainer,
        "payment_breakdown": payment_breakdown,
        "total_earnings": total_earnings,
        "total_paid": total_paid,
        "pending_amount": pending_amount,
        "total_trainees": trainee_assignments.count(),
        "payment_history": payment_history,
        "commission_rate": (
            float(trainer.commission_rate) if trainer.commission_rate else 30
        ),
    }

    return render(request, "trainer_template/payment_calculation.html", context)


@login_required(login_url="/")
def get_payment_summary(request):
    """API endpoint to get payment summary for dashboard"""
    trainer = get_object_or_404(Trainers, trainer_name=request.user)

    # Get trainee count
    total_trainees = TraineeCourseAssignment.objects.filter(trainer_id=trainer).count()

    # Calculate total earnings
    trainee_assignments = TraineeCourseAssignment.objects.filter(
        trainer_id=trainer
    ).select_related("course_id")

    total_earnings = 0
    for assignment in trainee_assignments:
        try:
            course_fee = (
                float(assignment.course_id.price) if assignment.course_id.price else 0
            )
            commission_rate = (
                float(trainer.commission_rate) / 100
                if trainer.commission_rate
                else 0.30
            )
            total_earnings += course_fee * commission_rate
        except (ValueError, TypeError):
            continue

    # Get total paid
    from .models import TrainerPayroll

    total_paid = 0
    for payroll in TrainerPayroll.objects.filter(trainer=trainer):
        try:
            total_paid += float(payroll.amount_paid) if payroll.amount_paid else 0
        except (ValueError, TypeError):
            continue

    pending_amount = total_earnings - total_paid

    return JsonResponse(
        {
            "total_trainees": total_trainees,
            "total_earnings": total_earnings,
            "total_paid": total_paid,
            "pending_amount": pending_amount,
            "commission_rate": (
                float(trainer.commission_rate) if trainer.commission_rate else 30
            ),
        }
    )
