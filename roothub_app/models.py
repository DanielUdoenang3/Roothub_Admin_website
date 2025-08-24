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
        (2, "Trainer"),
        (3, "Trainee"),
    )

    user_type = models.CharField(choices=USER_CHOICE, max_length=50, default=1)
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

class Trainers(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    skill_expertise = models.TextField(max_length=700)
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
    competent_skills = models.TextField()
    account_no = models.CharField(max_length=255, blank=True, null=True)
    bank = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    course_id = models.ManyToManyField('Courses', related_name='trainers')
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.trainer_name.first_name} {self.trainer_name.last_name}"

class Courses(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    course_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    months = models.CharField(max_length=200)
    number_of_presentation = models.CharField(max_length=100, blank=True, null=True)
    trainer_id = models.ForeignKey(Trainers, blank=True, null=True, on_delete=models.CASCADE)
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

class CourseLevelTrainer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    level_id = models.ForeignKey(Level, blank=True, null=True,on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, blank=True, null=True,on_delete=models.CASCADE)
    trainer_id = models.ForeignKey(Trainers, blank=True, null=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Trainee(models.Model):
    TRAINEE_CATEGORIES = [
        ('Regular', 'Regular Trainee'),
        ('SIWES', 'SIWES Intern'),
        ('Extern', 'Extern'),
        ('Triptern', 'Triptern'),
        ('Bootcamp', 'Bootcamp Kid'),
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
    matric_number = models.CharField(max_length=255, blank=True, null=True)
    duration_of_intership = models.CharField(max_length=255, blank=True, null=True)
    amount_paid = models.CharField(max_length=255, blank=True, null=True)
    date_of_payment = models.DateField(blank=True, null=True)
    commencement_date = models.DateField(blank=True, null=True)

    # Next of Kin(nok)
    nok_first_name = models.CharField(max_length=255, blank=True, null=True)
    nok_last_name = models.CharField(max_length=255, blank=True, null=True)
    nok_email = models.CharField(max_length=255, blank=True, null=True)
    nok_phone = models.CharField(max_length=255, blank=True, null=True)
    nok_relationship = models.CharField(max_length=255, blank=True, null=True)

    course_id = models.ForeignKey(Courses, on_delete=models.SET_NULL, related_name="trainees", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trainee {self.trainee_name.first_name} {self.trainee_name.last_name}'s details"

class TrainerCourseAssignment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE)

class TraineeCourseAssignment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainee_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    level_id = models.ForeignKey(Level, on_delete=models.CASCADE)
    
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

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    student_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class FeedBackTrainer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    student_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationTrainer(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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

    def __str__(self):
        return f"{self.title} - {self.description} at {self.class_date} during {self.start_class} to {self.end_class}"
    
class PaymentHistory(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    trainee_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment of {self.amount} for {self.course_id} by {self.trainee_id}"
    
class PaymentMethod(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    method_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.method_name

class PaymentTransaction(models.Model):
    Transaction_Status = (
        ('Success', 'Success'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed')
    )

    id = models.AutoField(primary_key=True, unique=True)
    payment_history = models.ForeignKey(PaymentHistory, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=Transaction_Status, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
class Payment(models.Model):
    id = models.AutoField(primary_key=True, unique=True)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admin.objects.create(admin_name=instance)
        if instance.user_type == 2:
            Trainers.objects.create(trainer_name=instance)
        if instance.user_type == 3:
            Trainee.objects.create(trainee_name=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admin.save()
    if instance.user_type == 2:
        instance.trainers.save()
    if instance.user_type == 3:
        instance.trainee.save()