from django.urls import path
from . import views

app_name = 'customize_admin'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('models/', views.models_list, name='models_list'),
    path('models/<str:app_label>/<str:model_name>/', views.model_detail, name='model_detail'),
    path('models/<str:app_label>/<str:model_name>/create/', views.model_create, name='model_create'),
path('models/<str:app_label>/<str:model_name>/<str:pk>/edit/', views.model_edit, name='model_edit'),
path('models/<str:app_label>/<str:model_name>/<str:pk>/delete/', views.model_delete, name='model_delete'),

    path('system-info/', views.system_info, name='system_info'),
]