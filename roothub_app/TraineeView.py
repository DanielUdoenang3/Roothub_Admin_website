from datetime import datetime
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, AssignmentSubmission, Attendance, AttendanceReport, Presentation_report, Trainers, Courses, Trainee
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse

@login_required(login_url="/")
def home(request):
    try:
        context=None
        trainee = get_object_or_404(Trainee, trainee_name=request.user)
        course = get_object_or_404(Courses, trainees=trainee)
        trainer = get_object_or_404(Trainers, course_id=course)
        if not trainer:
            messages.error(request,"There's no current trainer")
        context = {
            "course":course,
            "trainer":trainer,
        }
    except Exception:
        messages.error(request, "You cannot not access a Trainee Url")
    return render(request, "trainee_template/home.html", context)
@login_required(login_url="/")
def view_assignments(request):
    # Get trainee object
    trainee = get_object_or_404(Trainee, trainee_name=request.user)

    # Get all assignments for trainee's course
    assignments = Assignment.objects.filter(course=trainee.course_id)

    # Assignments the trainee has submitted
    submitted_assignments = AssignmentSubmission.objects.filter(trainee=trainee).values_list('assignment_id', flat=True)

    # Pending = assignments not submitted
    pending_assignments = assignments.exclude(id__in=submitted_assignments)

    context = {
        'pending_assignments': pending_assignments,
        'submitted_assignments': AssignmentSubmission.objects.filter(trainee=trainee),
        'pending_count': pending_assignments.count(),
        'submitted_count': AssignmentSubmission.objects.filter(trainee=trainee).count()
    }
    return render(request, 'trainee_template/view_assignment.html', context)

@login_required(login_url="/")
def submit_assignment(request, assignment_id):
    trainee=get_object_or_404(Trainee, trainee_name=request.user)
    assignment = get_object_or_404(Assignment, id=assignment_id)

    if request.method == 'POST':
        answer_text = request.POST.get('answer_text')
        answer_file = request.FILES.get('answer_file')

        AssignmentSubmission.objects.create(
            assignment=assignment,
            trainee=trainee,
            text_answer=answer_text,
            file=answer_file
        )
        messages.success(request, "Assignment submitted successfully")
        return redirect('view_assignments')

    return render(request, 'trainee_template/submit_assignment.html', {'assignment': assignment})

@login_required(login_url="/")
def view_trainee_presentation(request):
    trainee = get_object_or_404(Trainee, trainee_name=request.user)
    trainee_presentation = Presentation_report.objects.filter(trainee_id=trainee).select_related("presentation_id")
    presentation_dates = trainee_presentation.values_list("presentation_id__date", flat=True).distinct()

    content = {
        "presentation_report": trainee_presentation,
        "trainee": trainee,
        "presentation_dates": presentation_dates,
    }

    return render(request, "trainee_template/view_trainee_presentation.html", content)

@login_required(login_url="/")
def get_presentation_data_by_date(request, date):
    parsed_date = parse_date(date)

    if not parsed_date:
        return HttpResponseBadRequest("Invalid date format. Expected YYYY-MM-DD.")

    trainee = get_object_or_404(Trainee, trainee_name=request.user)
    presentations = Presentation_report.objects.filter(
        trainee_id=trainee, presentation_id__date=parsed_date
    ).select_related("presentation_id").values(
        "presentation_id__title",
        "presentation_id__score_appearance",
        "presentation_id__score_content",
        "presentation_id__comment",
    )

    # Add total_score calculation dynamically
    presentation_list = list(presentations)
    for presentation in presentation_list:
        score_appearance = presentation["presentation_id__score_appearance"] or 0
        score_content = presentation["presentation_id__score_content"] or 0
        presentation["total_score"] = score_appearance + score_content  # Add total score manually

    return JsonResponse({"presentations": presentation_list})

@login_required(login_url="/")
def view_trainee_attendance(request):
    trainee = get_object_or_404(Trainee, trainee_name=request.user)    
    trainee_attendance = AttendanceReport.objects.filter(student_id=trainee)

    content = {
        "attendance_report":trainee_attendance,
        "trainee": trainee,
    }
    return render(request, "trainee_template/view_trainee_attendance.html",content)

@login_required(login_url="/")
def get_trainee_attendance(request):
    trainee = request.user.trainee
    attendance_reports = AttendanceReport.objects.filter(student_id=trainee).select_related('attendance_id')

    attendance_data = {
        'dates': [report.attendance_id.attendance_date.strftime('%Y-%m-%d') for report in attendance_reports],
        'status': ['Present' if report.status else 'Absent' for report in attendance_reports],
    }

    return JsonResponse(attendance_data)