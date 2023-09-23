from django.urls import path
from manager import views


# urlpatterns = [
#     path('', views.list_apps, name="lister"),
#     path('build/', views.build_app, name="builder"),
#     path('<int:id>/', views.get_app, name="app-details"),
#     path('<int:id>/delete/', views.delete_app, name="app-delete"),
#     path('<int:id>/edit/', views.edit_app, name="editor"),
#     path('<int:id>/run/', views.run_app, name="runner"),
#     path('<int:id>/', views.history, name="run-history")
# ]

urlpatterns = [
    path('', views.ApplicationListApiView.as_view(), name="lister"),
    path('build/', views.BuildApplicationApiView.as_view(), name="builder"),
    path('<int:pk>/', views.ApplicationApiView.as_view(), name="app-details"),
    path('<int:pk>/run/', views.run_app, name="runner"),
    path('<int:id>/history/', views.RunLogsListApiView.as_view(), name="run-history")
]
