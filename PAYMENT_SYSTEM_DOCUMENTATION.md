# Payment Management System Documentation

## Overview
This comprehensive payment management system handles both trainee course payments and trainer salary payments with professional UI and robust backend functionality.

## Features Implemented

### 1. Trainee Payment Management
- **Payment Plans Supported:**
  - Full Payment (one-time payment)
  - 70% Upfront + 30% Later (two installments)
  - Monthly Payment (based on course duration)

- **Key Functionalities:**
  - View all trainees with payment status
  - Calculate total course fees (including level-based pricing)
  - Track payment history and outstanding amounts
  - Process individual installment payments
  - Support for different payment methods (Cash, Bank Transfer, Card)
  - Overdue payment detection

### 2. Trainer Payment Management
- **Salary Calculation Formula:**
  ```
  For each course/level:
  - Level Price = Course Price / Total Levels (if specific level)
  - Commission per Student = Level Price × (Commission Rate / 100)
  - Total Earned = Commission per Student × Number of Students
  ```

- **Key Functionalities:**
  - Monthly salary calculations based on students taught
  - Course and level breakdown for transparency
  - Payment history tracking
  - Support for deductions and adjustments
  - Monthly payment processing

### 3. Professional UI Components
- **Dashboard:** Choose between Trainee or Trainer payments
- **Search & Filter:** Find specific trainees/trainers quickly
- **Payment Details:** Comprehensive view of payment history
- **Process Payments:** Step-by-step payment processing
- **Progress Tracking:** Visual payment completion indicators

## File Structure

### Templates Created:
1. `templates/admin_template/payment.html` - Main payment dashboard
2. `templates/admin_template/trainee_payment_details.html` - Trainee payment history
3. `templates/admin_template/process_trainee_payment.html` - Process trainee payments
4. `templates/admin_template/trainer_payment_details.html` - Trainer payment history
5. `templates/admin_template/process_trainer_payment.html` - Process trainer payments

### Backend Files:
1. `roothub_app/payment_views.py` - All payment-related views
2. Updated `roothub_app/AdminView.py` - Import payment views
3. Updated `roothub_app/urls.py` - Payment URL patterns

## URL Patterns Added:
```python
# Trainee Payment Routes
path('trainee_payment_details/<int:trainee_id>/', ...)
path('process_trainee_payment/<int:trainee_id>/', ...)
path('process_trainee_payment_save/<int:trainee_id>/', ...)
path('process_installment_payment/<int:trainee_id>/<int:payment_id>/', ...)

# Trainer Payment Routes
path('trainer_payment_details/<int:trainer_id>/', ...)
path('process_trainer_payment/<int:trainer_id>/', ...)
path('process_trainer_payment_save/<int:trainer_id>/', ...)

# API Routes
path('api/trainer_payments/', ...)
```

## Key Functions Implemented:

### Trainee Payment Functions:
- `payment()` - Main dashboard with trainee/trainer selection
- `trainee_payment_details()` - Show detailed payment history
- `process_trainee_payment()` - Payment processing form
- `process_trainee_payment_save()` - Save payment data
- `process_installment_payment()` - Handle specific installments

### Trainer Payment Functions:
- `trainer_payment_details()` - Show trainer payment history
- `process_trainer_payment()` - Trainer payment processing
- `process_trainer_payment_save()` - Save trainer payment
- `calculate_trainer_salary()` - Calculate monthly salary
- `api_trainer_payments()` - AJAX endpoint for dynamic loading

## Payment Calculation Logic:

### Trainee Payments:
1. **Full Course:** Uses complete course price
2. **Level-based:** `(Course Price / Total Levels) × Selected Levels`
3. **Monthly:** `Total Fee / Course Duration in Months`
4. **70/30 Plan:** `70% upfront, 30% later`

### Trainer Payments:
1. Get all course/level assignments for trainer
2. Count students for each assignment in the target month
3. Calculate: `(Course/Level Price × Commission Rate) × Student Count`
4. Sum all earnings across all assignments

## Usage Instructions:

### For Trainee Payments:
1. Go to Payment Management
2. Select "Trainee Payments"
3. Find trainee and click "View" to see payment history
4. Click "Pay" to process outstanding payments
5. Select specific installment and enter payment details

### For Trainer Payments:
1. Go to Payment Management
2. Select "Trainer Payments"
3. Choose month/year and click "Load Payments"
4. View calculated salaries and click "Pay" to process
5. Review salary breakdown and confirm payment

## Security Features:
- Login required for all payment operations
- CSRF protection on all forms
- Input validation and error handling
- Transaction logging and audit trail

## Professional UI Features:
- Responsive design with Bootstrap
- Interactive cards and tables
- Progress bars and status badges
- Search and filter functionality
- Professional color scheme and icons
- Smooth animations and transitions

This system provides a complete, professional payment management solution that handles complex payment scenarios for both trainees and trainers with full transparency and audit capabilities.