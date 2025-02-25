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

    # Asssign Trainer
    path('assign_trainer', AdminView.assign_trainer, name="assign_trainer"),

]
