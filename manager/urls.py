from django.urls import path
from manager import views


urlpatterns = [
    path('', views.list_apps, name="lister"),
    path('build/', views.build_app, name="builder"),
    path('{id:pk}/', views.get_app, name="app-details"),
    path('{id:pk}/delete/', views.delete_app, name="app-delete"),
    path('{id:pk}/edit/', views.edit_app, name="editor"),
    path('{id:pk}/run/', views.run_app, name="runner"),
    path('history/', views.history, name="run-history")
]
