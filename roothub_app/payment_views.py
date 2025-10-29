# Payment Management Views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q, Count
from datetime import datetime, timedelta
from calendar import month_name
import calendar
from .models import *

@login_required(login_url="/")
def payment(request):
    # Get all trainees with payment calculations
    trainees = []
    for trainee in Trainee.objects.select_related('trainee_name', 'course_id').all():
        # Calculate total course fee
        if trainee.portion_type == "Level" and trainee.levels.exists():
            total_levels = Level.objects.filter(course_id=trainee.course_id).count()
            selected_levels = trainee.levels.count()
            per_level_price = float(trainee.course_id.price or 0) / total_levels if total_levels else 0
            total_course_fee = per_level_price * selected_levels
        else:
            total_course_fee = float(trainee.course_id.price or 0)
        
        # Calculate total amount paid
        payment_histories = PaymentHistory.objects.filter(trainee=trainee)
        total_amount_paid = 0
        for payment in payment_histories:
            if payment.amount_paid:
                try:
                    total_amount_paid += float(payment.amount_paid)
                except (ValueError, TypeError):
                    continue
        
        outstanding_amount = total_course_fee - total_amount_paid
        
        # Check for overdue payments
        has_overdue = False
        for payment in payment_histories:
            if payment.upfront_due_date and not payment.payment_date:
                if payment.upfront_due_date < datetime.now().date():
                    has_overdue = True
                    break
        
        trainee.total_course_fee = total_course_fee
        trainee.total_amount_paid = total_amount_paid
        trainee.outstanding_amount = outstanding_amount
        trainee.has_overdue = has_overdue
        trainees.append(trainee)
    
    # Get courses for filtering
    courses = Courses.objects.all()
    
    # Generate months and years for trainer payments
    current_date = datetime.now()
    months = [
        {'value': i, 'name': month_name[i]} 
        for i in range(1, 13)
    ]
    years = list(range(current_date.year - 2, current_date.year + 2))
    
    context = {
        'trainees': trainees,
        'courses': courses,
        'months': months,
        'years': years,
        'current_month': current_date.month,
        'current_year': current_date.year,
    }
    return render(request, 'admin_template/payment.html', context)

@login_required(login_url="/")
def trainee_payment_details(request, trainee_id):
    trainee = get_object_or_404(Trainee, id=trainee_id)
    payment_history = PaymentHistory.objects.filter(trainee=trainee).order_by('installmental_payment')
    
    # Calculate total course fee
    if trainee.portion_type == "Level" and trainee.levels.exists():
        total_levels = Level.objects.filter(course_id=trainee.course_id).count()
        selected_levels = trainee.levels.count()
        per_level_price = float(trainee.course_id.price or 0) / total_levels if total_levels else 0
        total_course_fee = per_level_price * selected_levels
    else:
        total_course_fee = float(trainee.course_id.price or 0)
    
    # Calculate total amount paid
    total_amount_paid = 0
    for payment in payment_history:
        if payment.amount_paid:
            try:
                total_amount_paid += float(payment.amount_paid)
            except (ValueError, TypeError):
                continue
    
    outstanding_amount = total_course_fee - total_amount_paid
    payment_percentage = (total_amount_paid / total_course_fee * 100) if total_course_fee > 0 else 0
    
    # Calculate monthly amount for monthly payments
    monthly_amount = 0
    if trainee.payment_option == "Monthly Payment" and trainee.course_id.months:
        course_months = int(trainee.course_id.months)
        monthly_amount = total_course_fee / course_months if course_months > 0 else 0
    
    # Calculate amounts for 70/30 plan
    upfront_amount = total_course_fee * 0.7
    final_amount = total_course_fee * 0.3
    
    context = {
        'trainee': trainee,
        'payment_history': payment_history,
        'total_course_fee': total_course_fee,
        'total_amount_paid': total_amount_paid,
        'outstanding_amount': outstanding_amount,
        'payment_percentage': payment_percentage,
        'monthly_amount': monthly_amount,
        'upfront_amount': upfront_amount,
        'final_amount': final_amount,
    }
    return render(request, 'admin_template/trainee_payment_details.html', context)

@login_required(login_url="/")
def process_trainee_payment(request, trainee_id):
    trainee = get_object_or_404(Trainee, id=trainee_id)
    
    # Get pending payments
    pending_payments = PaymentHistory.objects.filter(
        trainee=trainee
    ).filter(
        Q(amount_paid__isnull=True) | Q(amount_paid='0') | Q(amount_paid='')
    ).order_by('installmental_payment')
        
    # Calculate amounts
    if trainee.portion_type == "Level" and trainee.levels.exists():
        total_levels = Level.objects.filter(course_id=trainee.course_id).count()
        selected_levels = trainee.levels.count()
        per_level_price = float(trainee.course_id.price or 0) / total_levels if total_levels else 0
        total_course_fee = per_level_price * selected_levels
    else:
        total_course_fee = float(trainee.course_id.price or 0)
    
    total_amount_paid = 0
    for payment in PaymentHistory.objects.filter(trainee=trainee):
        if payment.amount_paid:
            try:
                total_amount_paid += float(payment.amount_paid)
            except (ValueError, TypeError):
                continue
    
    outstanding_amount = total_course_fee - total_amount_paid
    
    # Calculate specific amounts
    monthly_amount = 0
    if trainee.payment_option == "Monthly Payment" and trainee.course_id.months:
        course_months = int(trainee.course_id.months)
        monthly_amount = total_course_fee / course_months if course_months > 0 else 0
    
    upfront_amount = total_course_fee * 0.7
    final_amount = total_course_fee * 0.3
    
    context = {
        'trainee': trainee,
        'pending_payments': pending_payments,
        'total_course_fee': total_course_fee,
        'total_amount_paid': total_amount_paid,
        'outstanding_amount': outstanding_amount,
        'monthly_amount': monthly_amount,
        'upfront_amount': upfront_amount,
        'final_amount': final_amount,
        'today': datetime.now().date(),
    }
    return render(request, 'admin_template/process_trainee_payment.html', context)

@login_required(login_url="/")
def process_trainee_payment_save(request, trainee_id):
    if request.method == "POST":
        try:
            trainee = get_object_or_404(Trainee, id=trainee_id)
            payment_id = request.POST.get('payment_id')
            amount_paid = request.POST.get('amount_paid')
            payment_method = request.POST.get('payment_method')
            payment_date = request.POST.get('payment_date')
            reference_number = request.POST.get('reference_number', '')
            payment_notes = request.POST.get('payment_notes', '')
            
            # Get the payment record
            payment = get_object_or_404(PaymentHistory, id=payment_id, trainee=trainee)
            
            # Update payment record
            payment.amount_paid = amount_paid
            payment.payment_method = payment_method
            payment.payment_date = payment_date
            payment.save()
            
            messages.success(request, f"Payment of ₦{float(amount_paid):,.0f} processed successfully!")
            return redirect('trainee_payment_details', trainee_id=trainee_id)
            
        except Exception as e:
            print(f"Error processing payment: {e}")
            messages.error(request, "An error occurred while processing the payment.")
            return redirect('process_trainee_payment', trainee_id=trainee_id)
    
    return redirect('process_trainee_payment', trainee_id=trainee_id)

@login_required(login_url="/")
def process_installment_payment(request, trainee_id, payment_id):
    trainee = get_object_or_404(Trainee, id=trainee_id)
    payment = get_object_or_404(PaymentHistory, id=payment_id, trainee=trainee)
    
    # Redirect to the main payment processing page with specific payment
    return redirect('process_trainee_payment', trainee_id=trainee_id)

def calculate_trainer_salary(trainer, month, year):
    """Calculate trainer salary for a specific month/year"""
    commission_rate = float(trainer.commission_rate or 0) / 100
    total_salary = 0
    course_breakdown = []
    
    # Get all assignments for this trainer
    assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer).select_related('course_id', 'level_id')
    
    for assignment in assignments:
        course = assignment.course_id
        level = assignment.level_id
        
        # Get trainees for this course/level combination
        if level:
            # Specific level
            trainees = Trainee.objects.filter(
                course_id=course,
                levels=level,
                created_at__month=month,
                created_at__year=year
            )
            course_price = float(course.price or 0)
            total_levels = Level.objects.filter(course_id=course).count()
            level_price = course_price / total_levels if total_levels > 0 else course_price
        else:
            # Full course
            trainees = Trainee.objects.filter(
                course_id=course,
                portion_type="Full Course",
                created_at__month=month,
                created_at__year=year
            )
            course_price = float(course.price or 0)
            level_price = course_price
        
        student_count = trainees.count()
        if student_count > 0:
            commission_per_student = level_price * commission_rate
            total_earned = commission_per_student * student_count
            total_salary += total_earned
            
            course_breakdown.append({
                'course_name': course.course_name,
                'level_name': level.level if level else None,
                'student_count': student_count,
                'course_price': course_price,
                'level_price': level_price,
                'commission_per_student': commission_per_student,
                'total_earned': total_earned,
            })
    
    return total_salary, course_breakdown

@login_required(login_url="/")
def trainer_payment_details(request, trainer_id):
    trainer = get_object_or_404(Trainers, id=trainer_id)
    
    # Get payment history
    payment_history = TrainerPayroll.objects.filter(trainer=trainer).order_by('-year', '-month')
    
    # Get available years
    available_years = payment_history.values_list('year', flat=True).distinct()
    if not available_years:
        available_years = [datetime.now().year]
    
    # Calculate current month data
    current_date = datetime.now()
    current_month_salary, course_breakdown = calculate_trainer_salary(
        trainer, current_date.month, current_date.year
    )
    
    # Check if current month is already paid
    current_month_payroll = TrainerPayroll.objects.filter(
        trainer=trainer,
        month=str(current_date.month),
        year=str(current_date.year)
    ).first()
    
    current_month_paid = float(current_month_payroll.amount_paid or 0) if current_month_payroll else 0
    current_month_outstanding = current_month_salary - current_month_paid
    
    context = {
        'trainer': trainer,
        'payment_history': payment_history,
        'available_years': available_years,
        'current_year': current_date.year,
        'current_month_name': month_name[current_date.month],
        'current_month_salary': current_month_salary,
        'current_month_paid': current_month_paid,
        'current_month_outstanding': current_month_outstanding,
        'course_breakdown': course_breakdown,
        'total_courses': len(course_breakdown),
        'total_students': sum(c['student_count'] for c in course_breakdown),
    }
    return render(request, 'admin_template/trainer_payment_details.html', context)

@login_required(login_url="/")
def process_trainer_payment(request, trainer_id):
    trainer = get_object_or_404(Trainers, id=trainer_id)
    
    # Get month and year from query params or use current
    current_date = datetime.now()
    payment_month_num = int(request.GET.get('month', current_date.month))
    payment_year = int(request.GET.get('year', current_date.year))
    payment_month = month_name[payment_month_num]
    
    # Calculate salary for the specified month/year
    calculated_salary, salary_breakdown = calculate_trainer_salary(
        trainer, payment_month_num, payment_year
    )
    
    context = {
        'trainer': trainer,
        'payment_month': payment_month,
        'payment_month_num': payment_month_num,
        'payment_year': payment_year,
        'calculated_salary': calculated_salary,
        'salary_breakdown': salary_breakdown,
        'today': datetime.now().date(),
    }
    return render(request, 'admin_template/process_trainer_payment.html', context)

@login_required(login_url="/")
def process_trainer_payment_save(request, trainer_id):
    if request.method == "POST":
        try:
            trainer = get_object_or_404(Trainers, id=trainer_id)
            payment_month = request.POST.get('payment_month')
            payment_year = request.POST.get('payment_year')
            amount_paid = request.POST.get('amount_paid')
            payment_date = request.POST.get('payment_date')
            payment_method = request.POST.get('payment_method')
            reference_number = request.POST.get('reference_number', '')
            deductions = float(request.POST.get('deductions', 0))
            payment_notes = request.POST.get('payment_notes', '')
            
            # Calculate total salary
            calculated_salary, _ = calculate_trainer_salary(
                trainer, int(payment_month), int(payment_year)
            )
            
            # Create or update payroll record
            payroll, created = TrainerPayroll.objects.get_or_create(
                trainer=trainer,
                month=payment_month,
                year=payment_year,
                defaults={
                    'total_salary': str(calculated_salary),
                    'amount_paid': amount_paid,
                    'payment_date': payment_date,
                }
            )
            
            if not created:
                payroll.amount_paid = amount_paid
                payroll.payment_date = payment_date
                payroll.save()
            
            messages.success(request, f"Payment of ₦{float(amount_paid):,.0f} processed successfully for {trainer.trainer_name.get_full_name()}!")
            return redirect('trainer_payment_details', trainer_id=trainer_id)
            
        except Exception as e:
            print(f"Error processing trainer payment: {e}")
            messages.error(request, "An error occurred while processing the payment.")
            return redirect('process_trainer_payment', trainer_id=trainer_id)
    
    return redirect('process_trainer_payment', trainer_id=trainer_id)

@login_required(login_url="/")
def api_trainer_payments(request):
    """API endpoint for loading trainer payments dynamically"""
    month = int(request.GET.get('month') or datetime.now().month)
    year = int(request.GET.get('year') or datetime.now().year)
    
    trainers_data = []
    
    for trainer in Trainers.objects.all():
        # Calculate salary for the month
        calculated_salary, course_breakdown = calculate_trainer_salary(trainer, month, year)
        
        # Check if already paid
        payroll = TrainerPayroll.objects.filter(
            trainer=trainer,
            month=str(month),
            year=str(year)
        ).first()
        
        amount_paid = float(payroll.amount_paid or 0) if payroll else 0
        is_paid = amount_paid > 0
        
        # Get courses being taught
        assignments = TrainerCourseAssignment.objects.filter(trainer_id=trainer)
        courses = list(set([assignment.course_id.course_name for assignment in assignments]))
        
        # Count total students
        total_students = sum(c['student_count'] for c in course_breakdown)
        
        trainers_data.append({
            'id': trainer.id,
            'name': trainer.trainer_name.get_full_name(),
            'email': trainer.trainer_name.email,
            'profile_pic': trainer.trainer_name.profile_pic.url,
            'commission_rate': trainer.commission_rate or '0',
            'courses': courses,
            'total_students': total_students,
            'calculated_salary': calculated_salary,
            'amount_paid': amount_paid,
            'is_paid': is_paid,
        })
    
    return JsonResponse({'trainers': trainers_data})