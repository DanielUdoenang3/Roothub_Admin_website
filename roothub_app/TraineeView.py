from datetime import datetime
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Assignment, AssignmentSubmission, Fix_Class, AttendanceReport, Presentation_report, Trainers, Courses, Trainee, TraineeCourseAssignment
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse

@login_required(login_url="/")
def home(request):
    try:
        trainee = get_object_or_404(Trainee, trainee_name=request.user)
        
        # Get trainee's course and assignments
        course = trainee.course_id
        assignments = TraineeCourseAssignment.objects.filter(trainee_id=trainee).select_related('trainer_id', 'level_id')
        
        # Get all trainers for this trainee's course and levels
        trainers_info = []
        if assignments.exists():
            for assignment in assignments:
                trainer_info = {
                    'trainer': assignment.trainer_id,
                    'level': assignment.level_id,
                    'course': assignment.course_id
                }
                trainers_info.append(trainer_info)
        
        # Get course completion info
        course_completion_info = {
            'portion_type': trainee.portion_type,
            'portion_value': trainee.portion_value,
            'is_full_course': trainee.portion_type == 'Full Course',
            'completed': trainee.completed,
            'suspended': trainee.suspended,
            'terminated': trainee.terminated,
            'commencement_date': trainee.commencement_date,
            'end_date': trainee.end_date
        }
        
        # Get trainee's levels if doing partial course
        trainee_levels = trainee.levels.all() if trainee.portion_type == 'Level' else []
        
        # Get upcoming classes for trainee's course
        fix_classes = Fix_Class.objects.filter(course=course).order_by('class_date', 'start_class')[:5] if course else []
        
        # Calculate progress statistics
        total_assignments = Assignment.objects.filter(course=course).count() if course else 0
        completed_assignments = AssignmentSubmission.objects.filter(trainee=trainee).count()
        
        # Get recent attendance
        recent_attendance = AttendanceReport.objects.filter(student_id=trainee).order_by('-attendance_id__attendance_date')[:5]
        
        context = {
            "trainee": trainee,
            "course": course,
            "trainers_info": trainers_info,
            "course_completion_info": course_completion_info,
            "trainee_levels": trainee_levels,
            "fix_classes": fix_classes,
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "recent_attendance": recent_attendance,
            "progress_percentage": (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        }
    except Exception as e:
        print(f"Error in trainee home view: {e}")
        context = {
            "error": "Unable to load dashboard data"
        }
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

@login_required(login_url="/")
def view_payment_plan(request):
    """View payment plan details for trainee"""
    from .models import PaymentHistory
    from django.utils import timezone
    from datetime import timedelta
    
    trainee = get_object_or_404(Trainee, trainee_name=request.user)
    payment_history = PaymentHistory.objects.filter(trainee=trainee).order_by('-created_at')
    
    # Calculate payment summary
    total_amount_paid = 0
    for payment in payment_history:
        if payment.amount_paid:
            try:
                total_amount_paid += float(payment.amount_paid)
            except (ValueError, TypeError):
                continue
    
    # Get course fee
    course_price = 0
    if trainee.course_id and trainee.course_id.price:
        try:
            course_price = float(trainee.course_id.price)
        except (ValueError, TypeError):
            course_price = 0
    
    # Calculate remaining balance
    remaining_balance = course_price - total_amount_paid
    
    # Calculate monthly payment if applicable
    monthly_payment = 0
    if trainee.payment_option == "Monthly Payment" and trainee.course_id and trainee.course_id.months:
        try:
            monthly_payment = course_price / int(trainee.course_id.months)
        except (ValueError, TypeError, ZeroDivisionError):
            monthly_payment = 0
    
    # Get next payment due date (for notifications)
    next_due_date = None
    overdue_amount = 0
    
    # Find pending payments
    pending_payments = payment_history.filter(
        amount_paid__isnull=True
    ).order_by('expected_due_date')
    
    if pending_payments.exists():
        next_payment = pending_payments.first()
        next_due_date = next_payment.expected_due_date
        
        # Check if overdue
        if next_due_date and next_due_date < timezone.now().date():
            try:
                overdue_amount = float(next_payment.installmental_payment or 0)
            except (ValueError, TypeError):
                overdue_amount = 0
    
    # Payment progress percentage
    payment_progress = (total_amount_paid / course_price * 100) if course_price > 0 else 0
    
    context = {
        'trainee': trainee,
        'payment_history': payment_history,
        'total_course_fee': course_price,
        'total_amount_paid': total_amount_paid,
        'remaining_balance': remaining_balance,
        'monthly_payment': monthly_payment,
        'payment_progress': payment_progress,
        'next_due_date': next_due_date,
        'overdue_amount': overdue_amount,
        'is_overdue': overdue_amount > 0,
    }
    
    return render(request, 'trainee_template/payment_plan.html', context)

@login_required(login_url="/")
def payment_notifications_settings(request):
    """Manage payment notification preferences"""
    from .models import PaymentNotificationPreference
    
    trainee = get_object_or_404(Trainee, trainee_name=request.user)
    
    # Get or create notification preferences
    preferences_obj, created = PaymentNotificationPreference.objects.get_or_create(
        trainee=trainee,
        defaults={
            'email_notifications': True,
            'sms_notifications': False,
            'reminder_days': 7
        }
    )
    
    if request.method == 'POST':
        # Update notification preferences
        preferences_obj.email_notifications = request.POST.get('email_notifications') == 'on'
        preferences_obj.sms_notifications = request.POST.get('sms_notifications') == 'on'
        preferences_obj.reminder_days = int(request.POST.get('reminder_days', '7'))
        preferences_obj.save()
        
        messages.success(request, "Notification preferences updated successfully!")
        return redirect('payment_notifications_settings')
    
    context = {
        'trainee': trainee,
        'preferences': preferences_obj,
    }
    
    return render(request, 'trainee_template/payment_notifications.html', context)

@login_required(login_url="/")
def get_payment_notifications(request):
    """API endpoint to get payment notifications for trainee"""
    from django.utils import timezone
    from .models import PaymentHistory, PaymentNotificationPreference
    
    trainee = get_object_or_404(Trainee, trainee_name=request.user)
    
    # Get notification preferences
    try:
        preferences = PaymentNotificationPreference.objects.get(trainee=trainee)
        reminder_days = preferences.reminder_days
    except PaymentNotificationPreference.DoesNotExist:
        reminder_days = 7
    
    notifications = []
    
    # Check for upcoming payments
    pending_payments = PaymentHistory.objects.filter(
        trainee=trainee,
        amount_paid__isnull=True,
        expected_due_date__isnull=False
    ).order_by('expected_due_date')
    
    today = timezone.now().date()
    
    for payment in pending_payments:
        if payment.expected_due_date:
            days_until_due = (payment.expected_due_date - today).days
            
            # Overdue payments
            if days_until_due < 0:
                notifications.append({
                    'type': 'overdue',
                    'title': 'Payment Overdue',
                    'message': f'Your payment of ₦{payment.installmental_payment} was due on {payment.expected_due_date.strftime("%B %d, %Y")}',
                    'amount': payment.installmental_payment,
                    'due_date': payment.expected_due_date.isoformat(),
                    'priority': 'high'
                })
            
            # Upcoming payments (within reminder period)
            elif days_until_due <= reminder_days:
                notifications.append({
                    'type': 'upcoming',
                    'title': f'Payment Due in {days_until_due} day{"s" if days_until_due != 1 else ""}',
                    'message': f'Your payment of ₦{payment.installmental_payment} is due on {payment.expected_due_date.strftime("%B %d, %Y")}',
                    'amount': payment.installmental_payment,
                    'due_date': payment.expected_due_date.isoformat(),
                    'priority': 'medium' if days_until_due > 3 else 'high'
                })
    
    return JsonResponse({
        'notifications': notifications,
        'count': len(notifications)
    })