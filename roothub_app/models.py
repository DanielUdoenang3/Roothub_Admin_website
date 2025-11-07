from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings


class CustomUser(AbstractUser):
    USER_CHOICE = (
        (1, "Admin"),
        (4, "Sub Admin"),
        (2, "Trainer"),
        (3, "Trainee"),
    )

    user_type = models.CharField(max_length=50, choices=USER_CHOICE, default=1)
    profile_pic = models.ImageField(upload_to="profile_pic", default="blank.webp")
    middle_name = models.CharField(max_length=200, blank=True)

class Admin(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    admin_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True)
    personal_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.admin_name.first_name
    
class SubAdmin(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    sub_admin_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    address = models.TextField(blank=True)
    personal_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sub_admin_name.first_name} - Sub Admin"

class Trainers(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    skill_expertise = models.ManyToManyField('SkillExpertise', related_name='trainers', blank=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    country = models.CharField(max_length=255)
    birthday = models.DateField(max_length=255, blank=True, null=True)
    competent_skills = models.ManyToManyField('CompetentSkill', related_name='trainers', blank=True)
    account_no = models.CharField(max_length=255, blank=True, null=True)
    bank = models.CharField(max_length=255, blank=True, null=True)

    commission_rate = models.CharField(max_length=255, blank=True, null=True) #Newly Added

    trainer_assignment = models.ForeignKey('TrainerCourseAssignment', on_delete=models.CASCADE, related_name="trainer_assignment", blank=True, null=True)
    trainer_payroll = models.ForeignKey('TrainerPayroll', on_delete=models.CASCADE, related_name="trainer_payroll", blank=True, null=True)
    course_id = models.ManyToManyField('Courses', related_name='trainers', blank=True)
    skill_expertise = models.ManyToManyField('SkillExpertise', related_name='skill_expertise', blank=True)
    competent_skills = models.ManyToManyField('CompetentSkill', related_name='competent_skills', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trainer_name.first_name} {self.trainer_name.last_name}"

class SkillExpertise(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Skill Expertise"

class CompetentSkill(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255)
    skill_expertise = models.ForeignKey(SkillExpertise, on_delete=models.CASCADE, related_name='competent_skills')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.skill_expertise.name})"

    class Meta:
        unique_together = ['name', 'skill_expertise']

class Courses(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    course_name = models.CharField(max_length=255)
    price = models.CharField(max_length=100, blank=True, null=True)
    months = models.CharField(max_length=200)
    number_of_presentation = models.CharField(max_length=100, blank=True, null=True)
    trainer_id = models.ForeignKey(Trainers, blank=True, null=True, on_delete=models.CASCADE)
    level_id = models.ForeignKey('Level', blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return self.course_name

class Level(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    level = models.CharField(max_length=255)
    descriptions = models.CharField(max_length=1000, blank=True, null=True)
    course_id = models.ForeignKey(Courses, blank=True, null=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.level

class Trainee(models.Model):
    TRAINEE_CATEGORIES = [
        ('Regular', 'Regular Trainee'),
        ('SIWES', 'SIWES Intern'),
        ('Extern', 'Extern'),
        ('Triptern', 'Triptern'),
        ('Bootcamp', 'Bootcamp Kid'),
    ]

    COURSE_PORTION = [
        ('Full Course', 'Full Course'),
        ('Level', 'Level'),
    ]

    PAYMENT_OPTION = [
        ('Full Payment', 'Full Payment'),
        ('70% upfront and 30% later', '70% upfront and 30% later'),
        ('Monthly Payment', 'Monthly Payment'),
    ]
    
    id = models.AutoField(primary_key=True, unique=True)
    trainee_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=TRAINEE_CATEGORIES)
    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTION)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ]
    )
    country = models.CharField(max_length=255, blank=True, null=True)
    name_of_school = models.CharField(max_length=255, blank=True, null=True)
    course_of_study = models.CharField(max_length=255, blank=True, null=True)
    portion_type = models.CharField(max_length=100, choices=COURSE_PORTION, blank=True, null=True)
    portion_value = models.CharField(max_length=255, blank=True, null=True)
    matric_number = models.CharField(max_length=255, blank=True, null=True)
    duration_of_intership = models.CharField(max_length=255, blank=True, null=True)
    commencement_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True) # Newly Added

    # Next of Kin(nok)
    nok_first_name = models.CharField(max_length=255, blank=True, null=True)
    nok_last_name = models.CharField(max_length=255, blank=True, null=True)
    nok_email = models.CharField(max_length=255, blank=True, null=True)
    nok_phone = models.CharField(max_length=255, blank=True, null=True)
    nok_relationship = models.CharField(max_length=255, blank=True, null=True)

    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="trainees", blank=True, null=True)
    levels = models.ManyToManyField('Level', related_name="trainees", blank=True)
    paymenthistory_id = models.ForeignKey('PaymentHistory', on_delete=models.CASCADE, related_name="payment_history", blank=True, null=True)
    trainee_assignment = models.ForeignKey('TraineeCourseAssignment', on_delete=models.CASCADE, related_name="trainee_assignment", blank=True, null=True)
    completed = models.BooleanField(default=False)
    suspended = models.BooleanField(default=False)
    terminated =  models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trainee {self.trainee_name.first_name} {self.trainee_name.last_name}'s details"

class TrainerCourseAssignment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class TraineeCourseAssignment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainee_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Curriculum(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    file = models.FileField(upload_to='curriculum', blank=True, null=True)
    
class Attendance(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    trainees = models.ManyToManyField(Trainee, related_name="attendance_records")
    attendance_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Presentation(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="presentations")
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name="presentations")
    date = models.DateField(default=timezone.now)
    comment = models.TextField()
    score_appearance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    score_content = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    presentation_file = models.FileField(upload_to="presentation", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def percentage(self):
        return ((self.score_appearance + self.score_content) / 20) * 100

class Presentation_report(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainee_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    presentation_id = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Presentation Report for {self.trainee_id} - {self.presentation_id.title}"

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    student_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attendance Report for {self.student_id} - Status: {'Present' if self.status else 'Absent'}"

class Assignment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    trainer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='assignments', blank=True, null=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions", blank=True, null=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name="submissions")
    text_answer = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="submissions", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    def __str__(self):
        return f"{self.assignment.title} - {self.trainee.trainee_name.username}"

class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('General', 'General'),
        ('Trainers', 'Trainers'),
        ('Trainees', 'Trainees'),
        ('Course', 'Course'),
    ]
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file = models.FileField(upload_to='announcements', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='General')
    course = models.ForeignKey('Courses', null=True, blank=True, on_delete=models.SET_NULL)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="read_announcements", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} - {self.description}"

class Fix_Class(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=225)
    description = models.TextField()
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    class_date = models.DateField()
    start_class = models.TimeField()
    end_class = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.description} at {self.class_date} during {self.start_class} to {self.end_class}"

class Payment(models.Model):
    Transaction_Status = (
        ('Success', 'Success'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed')
    )

    id = models.AutoField(primary_key=True, unique=True)
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=Transaction_Status, default='Pending')
    commission_rate = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"

class PaymentHistory(models.Model):
    Payment_Method = (
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Card', 'Card')
    )
    
    PAYMENT_OPTION = [
        ('Full Payment', 'Full Payment'),
        ('70% upfront and 30% later', '70% upfront and 30% later'),
        ('Monthly Payment', 'Monthly Payment'),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name="payment_histories")
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="payment_histories")
    amount_paid = models.CharField(max_length=255)
    payment_option = models.CharField(max_length=100, choices=PAYMENT_OPTION, blank=True, null=True)
    upfront_due_date = models.DateField(blank=True, null=True)
    installmental_payment = models.CharField(max_length=255) #for monthly Payment Users and for 70% upfront and 30% later Users(2 installment)
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(max_length=255, choices=Payment_Method)
    
    # Enhanced fields for professional payment system
    reference_number = models.CharField(max_length=255, blank=True, null=True)  # Transaction reference
    payment_notes = models.TextField(blank=True, null=True)  # Additional notes
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_payments")  # Who processed the payment
    expected_due_date = models.DateField(blank=True, null=True)  # When payment was expected
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} by {self.trainee.trainee_name.username} for {self.course.course_name}"
    
    @property
    def is_paid(self):
        """Check if this installment is paid"""
        return self.amount_paid and float(self.amount_paid or 0) > 0
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        if not self.is_paid and self.expected_due_date:
            return self.expected_due_date < timezone.now().date()
        return False

class TrainerPayroll(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
    ]
    
    id = models.AutoField(primary_key=True, unique=True)
    trainer = models.ForeignKey(Trainers, on_delete=models.CASCADE, related_name="payrolls")
    month = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    total_salary = models.CharField(max_length=255)
    amount_paid = models.CharField(max_length=255)
    payment_date = models.DateField(blank=True, null=True)
    
    # Enhanced fields for professional payment system
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Bank Transfer')
    reference_number = models.CharField(max_length=255, blank=True, null=True)  # Transaction reference
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Tax, advance, etc.
    payment_notes = models.TextField(blank=True, null=True)  # Additional notes
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_trainer_payments")  # Who processed the payment
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payroll of {self.amount_paid} to {self.trainer.trainer_name.username} for {self.month}/{self.year}"
    
    @property
    def is_paid(self):
        """Check if trainer is paid for this month"""
        return self.amount_paid and float(self.amount_paid or 0) > 0
    
    @property
    def net_amount(self):
        """Calculate net amount after deductions"""
        total = float(self.total_salary or 0)
        deduction = float(self.deductions or 0)
        return total - deduction
    
    @property
    def month_name(self):
        """Get month name from month number"""
        try:
            from calendar import month_name
            return month_name[int(self.month)]
        except (ValueError, IndexError):
            return self.month

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin_name=instance)
        if instance.user_type == 2:
            Trainers.objects.create(trainer_name=instance)
        if instance.user_type == 3:
            Trainee.objects.create(trainee_name=instance)
        if instance.user_type == 4:
            SubAdmin.objects.create(sub_admin_name=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.trainers.save()
    if instance.user_type == 3:
        instance.trainee.save()
    if instance.user_type == 4:
        instance.sub_admin.save()