from django.urls import path
from roothub_project import settings
from roothub_app import TraineeView, TrainerView
from . import views, AdminView



urlpatterns = [
    path('admin_home',AdminView.home, name="admin_home"),
    path('',views.login_view, name="login_page"),
    path('doLogin', views.dologin, name="dologin"),
    path('doLogout', views.doLogout, name="doLogout"),
    path('profile', views.profile, name="profile"),
    path('profile_update/<admin>', views.profile_update, name="profile_update"),
    path('search', AdminView.search, name="search"),
    path('search_for_trainers', TrainerView.search, name="search_for_trainers"),
    path('api/trainers-trainees-per-month/', views.trainers_trainees_per_month, name='trainers_trainees_per_month'),
    path('api/male-female-number-of-trainees/', views.male_female_number_of_trainees, name='male_female_number_of_trainees'),
    path('api/male-female-number-of-trainers/', views.male_female_number_of_trainers, name='male_female_number_of_trainers'),    
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
    path('assign_trainee', AdminView.assign_trainee, name="assign_trainee"),
    path('get_current_trainer/<int:course_id>', AdminView.get_current_trainer, name='get_current_trainer'),
    path('get_trainer_assignments/<int:trainer_id>', AdminView.get_trainer_assignments, name='get_trainer_assignments'),
    path('remove_trainer_assignment/', AdminView.remove_trainer_assignment, name='remove_trainer_assignment'),

    # AJAX endpoints for dynamic assignment
    path('get_trainee_course/<int:trainee_id>/', AdminView.get_trainee_course, name='get_trainee_course'),
    path('get_course_trainers/<int:course_id>/', AdminView.get_course_trainers, name='get_course_trainers'),
    path('get_course_levels/<int:course_id>/', AdminView.get_course_levels, name='get_course_levels'),

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

    path('get-star_trainee-by-date/<str:date>/', views.star_trainee_view, name='star_trainees'),

    path('trainee_details/<username>/', AdminView.trainee_details, name='trainee_details'),
    path('trainer_details/<username>/', AdminView.trainer_details, name='trainer_details'),


    # Anouncement
    path('send_announcement', AdminView.send_announcement, name="send_announcement"),
    path('view_announcement', AdminView.view_announcement, name="view_announcement"),
    path('view_announcements', views.view_annoucements, name="view_announcements"),
    path('delete_announcement/<announcement_title>', AdminView.delete_announcement, name="delete_announcement"),
    path('edit_announcement/<announcement_title>', AdminView.edit_announcement, name="edit_announcement"),
    path('get-unread-announcements/', views.get_unread_announcements, name="get_unread_announcements"),
    path('mark-announcement-as-read/<int:announcement_id>/', views.mark_announcement_as_read, name="mark_announcement_as_read"),

    # Trainer Views
    path("trainer_home", TrainerView.home, name="trainer_home"),
    path("upload_assignment", TrainerView.upload_assignment, name="upload_assignment"),
    path("view_upload_assignment", TrainerView.view_uploaded_assignments, name="view_upload_assignment"),
    path("view_submissions", TrainerView.view_submissions, name="view_submissions"),
    path("edit_assignment/<id>", TrainerView.edit_assignment, name="edit_assignment"),
    path("delete_uploaded_assignment/<assignment_title>", TrainerView.delete_uploaded_assignment, name="delete_uploaded_assignment"),
    path("fix_classes", TrainerView.fix_classes, name="fix_classes"),

    
    # Trainee Views
    path("trainee_home", TraineeView.home, name="trainee_home"),
    path("view_assignments", TraineeView.view_assignments, name="view_assignments"),
    path('submit_assignment/<int:assignment_id>', TraineeView.submit_assignment, name='submit_assignment'),
    path("view_trainee_attendance", TraineeView.view_trainee_attendance, name="view_trainee_attendance"),
    path('get-trainee-attendance/', TraineeView.get_trainee_attendance, name='get_trainee_attendance'),
    path("view_trainee_presentation", TraineeView.view_trainee_presentation, name="view_trainee_presentation"),
    path('get-presentation-data-by-date/<str:date>/', TraineeView.get_presentation_data_by_date, name='get_presentation_data_by_date'),

    # Forgot Password
    path("forgot-password", views.forgot_password, name="forgot_password"),
    path(f"reset_password/<str:token>/", views.forgot_password_link, name="forgot_password_link"),

]

