from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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
    id = models.AutoField(primary_key=True)
    admin_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.admin_name.first_name

class Trainers(models.Model):
    id = models.AutoField(primary_key=True)
    trainer_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    religion = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    experience = models.CharField(max_length=700)
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
    created_at = models.DateTimeField(auto_now_add=True)
    course_id = models.ManyToManyField(
        'Courses',
        related_name='trainers')
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trainer {self.trainer_name.first_name} {self.trainer_name.last_name} details"

class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    trainer_id = models.ForeignKey(Trainers, blank=True, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return self.course_name

class Trainee(models.Model):
    id = models.AutoField(primary_key=True)
    trainee_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    gender = models.CharField(max_length=50, choices=[('Male', 'Male'), ('Female', 'Female')])
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    religion = models.CharField(max_length=255)
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
    course_id = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="trainees", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    def __str__(self):
        return f"Trainee {self.trainee_name.first_name} {self.trainee_name.last_name}'s details"

class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE)
    trainees = models.ManyToManyField(Trainee, related_name="attendance_records")
    attendance_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Presentation(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="presentations")
    trainee = models.ForeignKey(Trainee, on_delete=models.CASCADE, related_name="presentations")
    date = models.DateField(default=timezone.now)
    comment = models.TextField()
    score_appearance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    score_content = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class Presentation_report(models.Model):
    id = models.AutoField(primary_key=True)
    trainee_id = models.ForeignKey(Trainee, on_delete=models.DO_NOTHING)
    presentation_id = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class AttendanceReport(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    attendance_id = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attendance Report for {self.student_id} - Status: {'Present' if self.status else 'Absent'}"

class FeedBackStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Trainee, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class FeedBackTrainer(models.Model):
    id = models.AutoField(primary_key=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    feedback = models.TextField()
    feedback_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationStudent(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class NotificationTrainer(models.Model):
    id = models.AutoField(primary_key=True)
    trainer_id = models.ForeignKey(Trainers, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

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