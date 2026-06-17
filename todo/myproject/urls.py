from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add/', views.add_todo, name='add_todo'),
    path('toggle/<int:pk>/', views.toggle_todo, name='toggle_todo'),
    path('edit/<int:pk>/', views.edit_todo, name='edit_todo'),
    path('delete/<int:pk>/', views.delete_todo, name='delete_todo'),
    path('delete-completed/', views.delete_completed, name='delete_completed'),
]
