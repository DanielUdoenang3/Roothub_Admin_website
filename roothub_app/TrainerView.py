from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Trainers, Courses, Trainee


@login_required(login_url="/")
def home(request):
    trainer = Trainers.objects.get(trainer_name=request.user)
    courses = Courses.objects.filter(trainer_id=trainer).all()
    trainees_count = Trainee.objects.filter(course_id__in=courses).count()

    content = {
        'trainer': trainer,
        'courses': courses,
        'trainees_count': trainees_count,
    }
    return render(request, "trainer_template/home.html",content)