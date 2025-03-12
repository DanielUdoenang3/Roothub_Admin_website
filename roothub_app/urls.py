from django.urls import path

from roothub_app import TrainerView
from . import views, AdminView



urlpatterns = [
    path('admin_home',AdminView.home, name="admin_home"),
    path('',views.login_view, name="login_page"),
    path('doLogin', views.dologin, name="dologin"),
    path('doLogout', views.doLogout, name="doLogout"),
    path('profile', views.profile_update, name="profile"),
    path('search', AdminView.search, name="search"),


    # Trainer
    path('add_trainer', AdminView.add_trainer, name="add_trainer"),
    path('add_trainer_save', AdminView.add_trainer_save, name="add_trainer_save"),
    path('view_trainer', AdminView.view_trainer, name="view_trainer"),

    # Trainee
    path('add_trainee', AdminView.add_trainee, name="add_trainee"),
    path('add_trainee_save', AdminView.add_trainee_save, name="add_trainee_save"),
    path('view_trainee', AdminView.view_trainee, name="view_trainee"),

    # Course
    path('add_course', AdminView.add_course, name="add_course"),
    path('add_course_save', AdminView.add_course_save, name="add_course_save"),
    path('view_course', AdminView.view_course, name="view_course"),

    # Asssign Trainer
    path('assign_trainer', AdminView.assign_trainer, name="assign_trainer"),
    path('get_current_trainer/<int:course_id>', AdminView.get_current_trainer, name='get_current_trainer'),

    # Edit Trainer
    path('edit_trainer/<trainer>', AdminView.edit_trainer, name="edit_trainer"),

    # Delete Trainer
    path('delete_trainer/<trainer>', AdminView.delete_trainer, name="delete_trainer"),

    # Edit Trainee
    path('edit_trainee/<trainee>', AdminView.edit_trainee, name="edit_trainee"),

    # Delete Trainee
    path('delete_trainee/<trainee>', AdminView.delete_trainee, name="delete_trainee"),

    # Edit Courses
    path('edit_course/<course>', AdminView.edit_course, name="edit_course"),
    # Delete Course
    path('delete_course/<course>', AdminView.delete_course, name="delete_course"),


    # Mark Attendance
    path('mark_attendance', views.mark_attendance, name="mark_attendance"),
    path('get-trainees/', views.get_trainees, name='get-trainees'),

    # View Attendance
    path('view_attendance', views.view_attendance, name="view_attendance"),
    path('get-attendance-data/<trainee_id>/', views.get_attendance_data, name="get-attendance-data"),

    # Mark Presentation
    path('mark_presentation', views.mark_presentation, name="mark_presentation"),
    path('get-trainees-by-course/<course_id>/', views.get_trainees_by_course, name="get_trainees_by_course"),

    path('get-dates-by-trainee/<int:trainee_id>/', views.get_dates_by_trainee, name="get_dates_by_trainee"),

    # Fetch presentations by date
    path('get-presentations-by-date/<int:trainee_id>/<str:date>/', views.get_presentations_by_date, name="get_presentations_by_date"),
    # View Presentation
    path('view_presentation', views.view_presentation, name="view_presentation"),


    # Trainer Views
    path("trainer_home", TrainerView.home, name="trainer_home")
]
