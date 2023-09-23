from django.urls import path
from manager import views


urlpatterns = [
    path('', views.ApplicationListApiView.as_view(), name="lister"),
    path('build/', views.BuildApplicationApiView.as_view(), name="builder"),
    path('<int:pk>/', views.ApplicationApiView.as_view(), name="app-details"),
    path('<int:pk>/run/', views.run_app, name="runner"),
    path('<int:id>/history/', views.RunLogsListApiView.as_view(), name="run-history")
]
