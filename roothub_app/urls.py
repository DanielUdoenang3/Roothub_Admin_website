from django.urls import path
from . import views, AdminView



urlpatterns = [
    path('admin_home',AdminView.home, name="admin_home"),
    path('',views.login_view, name="login_page"),
    path('doLogin', views.dologin, name="dologin"),
    path('doLogout', views.doLogout, name="doLogout"),
    path('profile', views.profile_update, name="profile"),


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

    # Edit Trainee
    path('edit_trainee/<trainee>', AdminView.edit_trainee, name="edit_trainee"),

]
