from manager import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', views.ApplicationViewSet, basename='application')
urlpatterns = router.urls
