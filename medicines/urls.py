from django.urls import path
from . import views

urlpatterns = [
    path('', views.standard_view, name='standard'),
    path('accessibility/', views.accessibility_view, name='accessibility'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('scan/', views.scan_medicine, name='scan_medicine'),
    path('medicines/', views.get_all_medicines, name='get_all_medicines'),
    path('medicines/add/', views.add_medicine, name='add_medicine'),
    path('medicines/edit/<int:id>/', views.edit_medicine, name='edit_medicine'),
    path('medicines/delete/<int:id>/', views.delete_medicine, name='delete_medicine'),
]